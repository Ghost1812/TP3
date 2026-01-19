"""
XML Service - TP3
Recebe dados via Socket, cria XML, valida, persiste em PostgreSQL e envia webhook
Também expõe endpoints gRPC para BI Service
"""
import os
import subprocess
import sys

# Gerar arquivos Python a partir do proto se não existirem
try:
    import xml_service_pb2
except ImportError:
    print("Gerando arquivos Python a partir do proto...")
    subprocess.run([
        sys.executable, "-m", "grpc_tools.protoc",
        "-I.", "--python_out=.", "--grpc_python_out=.", "xml_service.proto"
    ], check=True)
    import xml_service_pb2
import socket
import json
import threading
import requests
import uuid
from datetime import datetime
from typing import Dict, List
from lxml import etree
from lxml.etree import Element, SubElement, tostring
import psycopg2
from psycopg2.extras import RealDictCursor
import grpc
from concurrent import futures
import xml_service_pb2
import xml_service_pb2_grpc

# Configuração
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", "5432"))
POSTGRES_DB = os.getenv("POSTGRES_DB", "tp3_db")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
SOCKET_PORT = int(os.getenv("SOCKET_PORT", "8888"))
GRPC_PORT = int(os.getenv("GRPC_PORT", "5000"))

def get_db_connection():
    """Cria conexão com PostgreSQL"""
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

def criar_xml(dados: List[Dict], mapper_version: str, id_requisicao: str) -> str:
    """Cria XML a partir dos dados processados"""
    # Criar elemento raiz
    root = Element("RelatorioConformidade")
    root.set("DataGeracao", datetime.now().strftime("%Y-%m-%d"))
    root.set("Versao", mapper_version)
    
    # Configuração
    config = SubElement(root, "Configuracao")
    config.set("ValidadoPor", f"XML_Service_{uuid.uuid4().hex[:8]}")
    config.set("Requisitante", f"Processador_{id_requisicao[:8]}")
    
    # Paises
    paises = SubElement(root, "Paises")
    
    for dado in dados:
        pais = SubElement(paises, "Pais")
        pais.set("IDInterno", dado.get("IDInterno", ""))
        pais.set("Nome", dado.get("Nome", dado.get("Ticker", "")))
        
        # Detalhes do país
        detalhes_pais = SubElement(pais, "DetalhesPais")
        
        populacao_milhoes = SubElement(detalhes_pais, "PopulacaoMilhoes")
        populacao_milhoes.text = str(dado.get("PopulacaoMilhoes", dado.get("PrecoAtual", "0")))
        
        populacao_total = SubElement(detalhes_pais, "PopulacaoTotal")
        populacao_total.text = str(dado.get("PopulacaoTotal", dado.get("Volume", "0")))
        
        # Dados geográficos
        dados_geograficos = SubElement(pais, "DadosGeograficos")
        continente = SubElement(dados_geograficos, "Continente")
        continente.text = dado.get("Continente", dado.get("Tipo", "Desconhecido"))
        
        # Campos opcionais da API externa - sempre adicionar, mesmo se N/A
        subregiao = SubElement(dados_geograficos, "Subregiao")
        subregiao_val = dado.get("Subregiao", "N/A")
        subregiao.text = str(subregiao_val) if subregiao_val and subregiao_val != "N/A" else "N/A"
        
        capital = SubElement(dados_geograficos, "Capital")
        capital_val = dado.get("Capital", "N/A")
        capital.text = str(capital_val) if capital_val and capital_val != "N/A" else "N/A"
        
        moeda = SubElement(dados_geograficos, "Moeda")
        moeda_val = dado.get("Moeda", "N/A")
        moeda.text = str(moeda_val) if moeda_val and moeda_val != "N/A" else "N/A"
        
        densidade = SubElement(dados_geograficos, "DensidadePopulacao")
        densidade_val = dado.get("DensidadePopulacao", 0)
        densidade.text = str(densidade_val) if densidade_val and densidade_val != 0 else "0"
        
        # Histórico da API
        historico = SubElement(pais, "HistoricoAPI")
        
        media_30d = SubElement(historico, "Media30d")
        media_30d.text = str(dado.get("Media30d", "0"))
        
        maximo_6m = SubElement(historico, "Maximo6m")
        maximo_6m.text = str(dado.get("Maximo6m", "0"))
    
    # Converter para string XML
    xml_string = etree.tostring(root, encoding='unicode', pretty_print=True, xml_declaration=False)
    # Adicionar declaração XML manualmente
    xml_string = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_string
    return xml_string

def validar_xml(xml_string: str):
    """Valida XML"""
    try:
        etree.fromstring(xml_string.encode('utf-8'))
        return True, "XML válido"
    except etree.XMLSyntaxError as e:
        return False, f"Erro de validação: {str(e)}"

def persistir_xml(xml_string: str, mapper_version: str, id_requisicao: str):
    """Persiste XML no PostgreSQL"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO documentos_xml (xml_documento, mapper_version, id_requisicao, status)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (xml_string, mapper_version, id_requisicao, "OK")
        )
        
        documento_id = cursor.fetchone()[0]
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return True, documento_id, "OK"
        
    except Exception as e:
        return False, 0, f"ERRO_PERSISTENCIA: {str(e)}"

def enviar_webhook(webhook_url: str, id_requisicao: str, status: str, documento_id: int):
    """Envia webhook para Processador"""
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
    """Processa requisição recebida via Socket"""
    try:
        print(f"\nConexao recebida de {addr}")
        
        # Receber tamanho da mensagem (4 bytes)
        tamanho_bytes = conn.recv(4)
        if len(tamanho_bytes) < 4:
            raise ValueError("Tamanho da mensagem invalido")
        
        tamanho = int.from_bytes(tamanho_bytes, byteorder='big')
        
        # Receber mensagem completa
        dados_recebidos = b''
        while len(dados_recebidos) < tamanho:
            chunk = conn.recv(tamanho - len(dados_recebidos))
            if not chunk:
                raise ValueError("Conexao fechada antes de receber todos os dados")
            dados_recebidos += chunk
        
        # Decodificar JSON
        mensagem = json.loads(dados_recebidos.decode('utf-8'))
        
        id_requisicao = mensagem.get("id_requisicao")
        mapper = mensagem.get("mapper", {})
        mapper_version = mensagem.get("mapper_version", "1.0")
        webhook_url = mensagem.get("webhook_url")
        dados = mensagem.get("dados", [])
        
        print(f"Processando requisicao: {id_requisicao}")
        print(f"   Registros: {len(dados)}")
        
        # Criar XML
        xml_string = criar_xml(dados, mapper_version, id_requisicao)
        print("XML criado")
        
        # Validar XML
        valido, msg_validacao = validar_xml(xml_string)
        if not valido:
            print(f"{msg_validacao}")
            resposta = {"status": "ERRO_VALIDACAO", "erro": msg_validacao}
            enviar_webhook(webhook_url, id_requisicao, "ERRO_VALIDACAO", 0)
        else:
            print("XML validado")
            
            # Persistir no banco
            sucesso, documento_id, status = persistir_xml(xml_string, mapper_version, id_requisicao)
            
            if sucesso:
                print(f"XML persistido no banco. ID: {documento_id}")
                resposta = {"status": "OK", "documento_id": documento_id}
                enviar_webhook(webhook_url, id_requisicao, "OK", documento_id)
            else:
                print(f"{status}")
                resposta = {"status": "ERRO_PERSISTENCIA", "erro": status}
                enviar_webhook(webhook_url, id_requisicao, "ERRO_PERSISTENCIA", 0)
        
        # Enviar resposta
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
            # Enviar resposta de erro
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
    """Servidor Socket para receber dados do Processador"""
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

class XMLServiceServicer(xml_service_pb2_grpc.XMLServiceServicer):
    """Serviço gRPC para consultas do BI Service"""
    
    def ConsultarXPath(self, request, context):
        """Consulta XPath no banco de dados"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Executar função XPath do PostgreSQL
            cursor.execute(
                "SELECT * FROM consultar_xpath(%s, %s, %s, %s)",
                (request.xpath, request.id_requisicao or None, None, None)
            )
            
            resultados = [str(row['resultado']) for row in cursor.fetchall()]
            
            cursor.close()
            conn.close()
            
            return xml_service_pb2.XPathResponse(
                sucesso=True,
                resultados=resultados
            )
            
        except Exception as e:
            return xml_service_pb2.XPathResponse(
                sucesso=False,
                erro=str(e)
            )
    
    def AgregarAtivos(self, request, context):
        """Agrega ativos usando XMLTABLE"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(
                "SELECT * FROM agregar_ativos(%s, %s, %s)",
                (request.tipo or None, None, None)
            )
            
            ativos = []
            for row in cursor.fetchall():
                # ticker contém o IDInterno, tipo contém o nome do país
                ativo = xml_service_pb2.Ativo(
                    ticker=row['ticker'] or '',  # IDInterno
                    tipo=row['tipo'] or '',  # Nome do país
                    preco_atual=float(row['preco_atual'] or 0),
                    volume=int(row['volume'] or 0),
                    media_30d=float(row['media_30d'] or 0),
                    maximo_6m=float(row['maximo_6m'] or 0),
                    capital=row.get('capital') or '',
                    subregiao=row.get('subregiao') or '',
                    moeda=row.get('moeda') or '',
                    densidade=float(row.get('densidade') or 0)
                )
                ativos.append(ativo)
            
            cursor.close()
            conn.close()
            
            return xml_service_pb2.AgregarAtivosResponse(
                sucesso=True,
                ativos=ativos
            )
            
        except Exception as e:
            return xml_service_pb2.AgregarAtivosResponse(
                sucesso=False,
                erro=str(e)
            )
    
    def ContarAtivosPorTipo(self, request, context):
        """Conta ativos por tipo"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT * FROM contar_ativos_por_tipo(%s, %s)", (None, None))
            
            contagens = []
            for row in cursor.fetchall():
                contagem = xml_service_pb2.ContagemTipo(
                    tipo=row['tipo'] or '',
                    total=int(row['total'] or 0)
                )
                contagens.append(contagem)
            
            cursor.close()
            conn.close()
            
            return xml_service_pb2.ContarAtivosPorTipoResponse(
                sucesso=True,
                contagens=contagens
            )
            
        except Exception as e:
            return xml_service_pb2.ContarAtivosPorTipoResponse(
                sucesso=False,
                erro=str(e)
            )
    
    def MediaPrecosPorTipo(self, request, context):
        """Calcula média de preços por tipo"""
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("SELECT * FROM media_precos_por_tipo(%s, %s)", (None, None))
            
            medias = []
            for row in cursor.fetchall():
                media = xml_service_pb2.MediaPreco(
                    tipo=row['tipo'] or '',
                    media_preco=float(row['media_preco'] or 0)
                )
                medias.append(media)
            
            cursor.close()
            conn.close()
            
            return xml_service_pb2.MediaPrecosPorTipoResponse(
                sucesso=True,
                medias=medias
            )
            
        except Exception as e:
            return xml_service_pb2.MediaPrecosPorTipoResponse(
                sucesso=False,
                erro=str(e)
            )

def servidor_grpc():
    """Servidor gRPC para consultas do BI Service"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    xml_service_pb2_grpc.add_XMLServiceServicer_to_server(
        XMLServiceServicer(), server
    )
    server.add_insecure_port(f'0.0.0.0:{GRPC_PORT}')
    server.start()
    print(f"Servidor gRPC iniciado na porta {GRPC_PORT}")
    server.wait_for_termination()

def main():
    """Função principal"""
    print("=" * 60)
    print("XML SERVICE - TP3")
    print("=" * 60)
    print(f"PostgreSQL: {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
    print(f"Socket: 0.0.0.0:{SOCKET_PORT}")
    print(f"gRPC: 0.0.0.0:{GRPC_PORT}")
    print("=" * 60)
    
    # Iniciar servidor Socket em thread separada
    socket_thread = threading.Thread(target=servidor_socket, daemon=True)
    socket_thread.start()
    
    # Iniciar servidor gRPC (bloqueante)
    servidor_grpc()

if __name__ == "__main__":
    main()
