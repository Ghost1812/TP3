import grpc
from concurrent import futures
from psycopg2.extras import RealDictCursor
from db import get_db_connection
from config import GRPC_PORT
import xml_service_pb2
import xml_service_pb2_grpc

class XMLServiceServicer(xml_service_pb2_grpc.XMLServiceServicer):
    """
    Servico gRPC para consultas do BI Service
    Implementa metodos para consultar XMLs usando funcoes SQL
    """
    
    def ConsultarXPath(self, request, context):
        """
        Consulta XPath no banco de dados
        Usa apenas o XML mais recente
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
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
        """
        Agrega ativos usando XMLTABLE
        Extrai dados de paises do XML mais recente
        """
        try:
            conn = get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            tipo_filtro = request.tipo or None
            MAX_REGISTROS = 5000
            print(f"AgregarAtivos chamado com tipo: {tipo_filtro}, limite: {MAX_REGISTROS}")
            
            cursor.execute(
                f"SELECT * FROM agregar_ativos(%s, %s, %s) LIMIT {MAX_REGISTROS}",
                (tipo_filtro, None, None)
            )
            
            ativos = []
            for row in cursor.fetchall():
                try:
                    ativo = xml_service_pb2.Ativo(
                        ticker=row['ticker'] or '',
                        tipo=row['tipo'] or '',
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
                except Exception as e:
                    print(f"Erro ao processar linha: {e}, dados: {row}")
                    continue
            
            cursor.close()
            conn.close()
            
            print(f"AgregarAtivos retornou {len(ativos)} ativos")
            
            return xml_service_pb2.AgregarAtivosResponse(
                sucesso=True,
                ativos=ativos
            )
        except Exception as e:
            print(f"Erro em AgregarAtivos: {e}")
            import traceback
            traceback.print_exc()
            return xml_service_pb2.AgregarAtivosResponse(
                sucesso=False,
                erro=str(e)
            )
    
    def ContarAtivosPorTipo(self, request, context):
        """
        Conta ativos por tipo (continente)
        Retorna contagem de paises unicos por regiao
        """
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
        """
        Calcula media de populacao por tipo (continente)
        """
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
    """
    Servidor gRPC para consultas do BI Service
    Configura limites de tamanho de mensagem para suportar XMLs grandes
    """
    options = [
        ('grpc.max_receive_message_length', 30 * 1024 * 1024),
        ('grpc.max_send_message_length', 30 * 1024 * 1024),
    ]
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=options)
    xml_service_pb2_grpc.add_XMLServiceServicer_to_server(
        XMLServiceServicer(), server
    )
    server.add_insecure_port(f'0.0.0.0:{GRPC_PORT}')
    server.start()
    print(f"Servidor gRPC iniciado na porta {GRPC_PORT}")
    server.wait_for_termination()
