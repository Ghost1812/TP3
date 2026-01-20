import socket
import json
import threading
import requests
from xml_builder import criar_xml, validar_xml
from db import persistir_xml
from config import SOCKET_PORT

def enviar_webhook(webhook_url: str, id_requisicao: str, status: str, documento_id: int):
    """
    Envia webhook para Processador com status da persistencia
    """
    try:
        payload = {
            "id_requisicao": id_requisicao,
            "status": status,
            "documento_id": documento_id
        }
        response = requests.post(webhook_url, json=payload, timeout=10)
        print(f"Webhook enviado para {webhook_url}: {status}")
        return response.status_code == 200
    except Exception as e:
        print(f"Erro ao enviar webhook: {e}")
        return False

def processar_requisicao_socket(conn: socket.socket, addr: tuple):
    """
    Processa requisicao recebida via Socket TCP
    Cria XML, valida e persiste no banco de dados
    """
    try:
        print(f"\nConexao recebida de {addr}")
        
        tamanho_bytes = conn.recv(4)
        if len(tamanho_bytes) < 4:
            raise ValueError("Tamanho da mensagem invalido")
        
        tamanho = int.from_bytes(tamanho_bytes, byteorder='big')
        
        dados_recebidos = b''
        while len(dados_recebidos) < tamanho:
            chunk = conn.recv(tamanho - len(dados_recebidos))
            if not chunk:
                raise ValueError("Conexao fechada antes de receber todos os dados")
            dados_recebidos += chunk
        
        mensagem = json.loads(dados_recebidos.decode('utf-8'))
        
        id_requisicao = mensagem.get("id_requisicao")
        mapper_version = mensagem.get("mapper_version", "1.0")
        webhook_url = mensagem.get("webhook_url")
        dados = mensagem.get("dados", [])
        
        print(f"Processando requisicao: {id_requisicao}")
        print(f"   Registros: {len(dados)}")
        
        xml_string = criar_xml(dados, mapper_version, id_requisicao)
        print("XML criado")
        
        valido, msg_validacao = validar_xml(xml_string)
        if not valido:
            print(f"{msg_validacao}")
            resposta = {"status": "ERRO_VALIDACAO", "erro": msg_validacao}
            enviar_webhook(webhook_url, id_requisicao, "ERRO_VALIDACAO", 0)
        else:
            print("XML validado")
            sucesso, documento_id, status = persistir_xml(xml_string, mapper_version, id_requisicao)
            
            if sucesso:
                print(f"XML persistido no banco. ID: {documento_id}")
                resposta = {"status": "OK", "documento_id": documento_id}
                enviar_webhook(webhook_url, id_requisicao, "OK", documento_id)
            else:
                print(f"{status}")
                resposta = {"status": "ERRO_PERSISTENCIA", "erro": status}
                enviar_webhook(webhook_url, id_requisicao, "ERRO_PERSISTENCIA", 0)
        
        resposta_json = json.dumps(resposta)
        resposta_bytes = resposta_json.encode('utf-8')
        conn.sendall(len(resposta_bytes).to_bytes(4, byteorder='big'))
        conn.sendall(resposta_bytes)
        conn.close()
        
    except Exception as e:
        print(f"Erro ao processar requisicao: {e}")
        import traceback
        traceback.print_exc()
        try:
            resposta_erro = {"status": "ERRO", "erro": str(e)}
            resposta_json = json.dumps(resposta_erro)
            resposta_bytes = resposta_json.encode('utf-8')
            conn.sendall(len(resposta_bytes).to_bytes(4, byteorder='big'))
            conn.sendall(resposta_bytes)
            conn.close()
        except:
            try:
                conn.close()
            except:
                pass

def servidor_socket():
    """
    Servidor Socket TCP para receber dados do Processador
    Aceita conexoes e processa em threads separadas
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('0.0.0.0', SOCKET_PORT))
    sock.listen(5)
    
    print(f"Servidor Socket iniciado na porta {SOCKET_PORT}")
    
    while True:
        conn, addr = sock.accept()
        thread = threading.Thread(target=processar_requisicao_socket, args=(conn, addr))
        thread.daemon = True
        thread.start()
