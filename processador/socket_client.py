import socket
import json
from config import XML_SERVICE_HOST, XML_SERVICE_PORT, MAPPER_VERSION, WEBHOOK_URL


def enviar_para_xml_service(id_requisicao: str, mapper: dict, webhook_url: str, dados: list) -> bool:
    """
    Envia os dados processados para o XML Service através de um socket TCP.
    """
    try:
        # Cria a mensagem a enviar para o XML Service
        mensagem = {
            "id_requisicao": id_requisicao,
            "mapper": mapper,
            "mapper_version": MAPPER_VERSION,
            "webhook_url": webhook_url,
            "dados": dados
        }

        # Converte a mensagem para JSON e depois para bytes
        mensagem_json = json.dumps(mensagem)
        mensagem_bytes = mensagem_json.encode('utf-8')

        # Cria o socket TCP
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)

        # Estabelece ligação ao XML Service
        print(f"Conectando ao XML Service em {XML_SERVICE_HOST}:{XML_SERVICE_PORT}...")
        sock.connect((XML_SERVICE_HOST, XML_SERVICE_PORT))

        # Envia primeiro o tamanho da mensagem
        tamanho = len(mensagem_bytes)
        sock.sendall(tamanho.to_bytes(4, byteorder='big'))

        # Envia a mensagem propriamente dita
        sock.sendall(mensagem_bytes)

        # Recebe o tamanho da resposta
        resposta_tamanho = int.from_bytes(sock.recv(4), byteorder='big')

        # Recebe a resposta do XML Service
        resposta_bytes = sock.recv(resposta_tamanho)
        resposta = json.loads(resposta_bytes.decode('utf-8'))

        # Fecha o socket
        sock.close()

        # Verifica se o envio foi bem-sucedido
        if resposta.get("status") == "OK":
            print(f"Dados enviados com sucesso. ID Requisicao: {id_requisicao}")
            return True
        else:
            print(f"Erro ao enviar dados: {resposta.get('erro', 'Erro desconhecido')}")
            return False

    except Exception as e:
        # Erro de ligação ou comunicação com o XML Service
        print(f"Erro ao conectar ao XML Service: {e}")
        return False
