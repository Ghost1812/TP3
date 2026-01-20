"""
Processador Service - TP3
Inicia Flask e loop de monitoramento do bucket Supabase
"""
import os
import time
import threading
import uuid
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET, XML_SERVICE_HOST, XML_SERVICE_PORT, WEBHOOK_URL, MAX_ARQUIVOS_BUCKET, MAPPER
from bucket_monitor import monitorizar_bucket, marcar_processado, gerenciar_fifo
from csv_processor import processar_csv_stream
from socket_client import enviar_para_xml_service
from webhook_server import app

def processar_arquivo(nome_arquivo: str):
    """
    Processa um arquivo CSV do bucket Supabase
    Baixa, processa e envia para XML Service
    """
    try:
        print(f"\nProcessando arquivo: {nome_arquivo}")
        
        # Gerencia FIFO antes de processar (garante maximo 3 arquivos)
        gerenciar_fifo()
        
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        csv_bytes = supabase.storage.from_(SUPABASE_BUCKET).download(nome_arquivo)
        
        print(f"Arquivo baixado: {len(csv_bytes)} bytes")
        
        dados_processados = processar_csv_stream(csv_bytes)
        print(f"Processados {len(dados_processados)} registros")
        
        id_requisicao = str(uuid.uuid4())
        
        sucesso = enviar_para_xml_service(
            id_requisicao=id_requisicao,
            mapper=MAPPER,
            webhook_url=WEBHOOK_URL,
            dados=dados_processados
        )
        
        if sucesso:
            marcar_processado(nome_arquivo)
            # Gerencia FIFO novamente apos processar
            gerenciar_fifo()
        else:
            print(f"Falha ao processar arquivo: {nome_arquivo}")
            
    except Exception as e:
        print(f"Erro ao processar arquivo {nome_arquivo}: {e}")
        import traceback
        traceback.print_exc()

def loop_monitoramento():
    """
    Loop principal de monitoramento
    Verifica bucket a cada 10 segundos por novos arquivos CSV
    """
    print("=" * 60)
    print("PROCESSADOR SERVICE - TP3")
    print("=" * 60)
    print(f"Supabase Bucket: {SUPABASE_BUCKET}")
    print(f"XML Service: {XML_SERVICE_HOST}:{XML_SERVICE_PORT}")
    print(f"Webhook URL: {WEBHOOK_URL}")
    print("=" * 60)
    
    while True:
        try:
            novos_arquivos = monitorizar_bucket()
            
            if novos_arquivos:
                print(f"\nEncontrados {len(novos_arquivos)} novo(s) arquivo(s)")
                for arquivo in novos_arquivos:
                    processar_arquivo(arquivo)
            else:
                print(".", end="", flush=True)
            
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\n\nProcessador interrompido pelo usuario")
            break
        except Exception as e:
            print(f"\nErro no loop de monitoramento: {e}")
            time.sleep(10)

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", "5001"))
    
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=PORT, debug=False), daemon=True)
    flask_thread.start()
    
    loop_monitoramento()
