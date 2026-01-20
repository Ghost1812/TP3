import socket
import json
from config import XML_SERVICE_HOST, XML_SERVICE_PORT, MAPPER_VERSION, WEBHOOK_URL

def enviar_para_xml_service(id_requisicao: str, mapper: dict, webhook_url: str, dados: list) -> bool:
    """Envia dados para XML Service via Socket"""
    try:
        mensagem = {
            "id_requisicao": id_requisicao,
            "mapper": mapper,
            "mapper_version": MAPPER_VERSION,
            "webhook_url": webhook_url,
            "dados": dados
        }
        
        mensagem_json = json.dumps(mensagem)
        mensagem_bytes = mensagem_json.encode('utf-8')
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        
        print(f"Conectando ao XML Service em {XML_SERVICE_HOST}:{XML_SERVICE_PORT}...")
        sock.connect((XML_SERVICE_HOST, XML_SERVICE_PORT))
        
        tamanho = len(mensagem_bytes)
        sock.sendall(tamanho.to_bytes(4, byteorder='big'))
        sock.sendall(mensagem_bytes)
        
        resposta_tamanho = int.from_bytes(sock.recv(4), byteorder='big')
        resposta_bytes = sock.recv(resposta_tamanho)
        resposta = json.loads(resposta_bytes.decode('utf-8'))
        
        sock.close()
        
        if resposta.get("status") == "OK":
            print(f"Dados enviados com sucesso. ID Requisicao: {id_requisicao}")
            return True
        else:
            print(f"Erro ao enviar dados: {resposta.get('erro', 'Erro desconhecido')}")
            return False
            
    except Exception as e:
        print(f"Erro ao conectar ao XML Service: {e}")
        return False
