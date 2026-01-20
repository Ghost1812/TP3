from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET, MAX_ARQUIVOS_BUCKET

arquivos_processados = set()

def monitorizar_bucket():
    """Monitoriza bucket do Supabase por novos arquivos"""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        arquivos = supabase.storage.from_(SUPABASE_BUCKET).list()
        
        novos_arquivos = []
        for arquivo in arquivos:
            if arquivo['name'].endswith('.csv') and arquivo['name'] not in arquivos_processados:
                novos_arquivos.append(arquivo['name'])
        
        return novos_arquivos
    except Exception as e:
        print(f"Erro ao monitorizar bucket: {e}")
        return []

def marcar_processado(nome_arquivo: str):
    """Marca arquivo como processado"""
    arquivos_processados.add(nome_arquivo)

def gerenciar_fifo():
    """Gerencia FIFO: remove arquivo mais antigo se houver 3 ou mais"""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        arquivos = supabase.storage.from_(SUPABASE_BUCKET).list()
        csvs = [f for f in arquivos if f['name'].endswith('.csv')]
        
        if len(csvs) >= MAX_ARQUIVOS_BUCKET:
            csvs_ordenados = sorted(csvs, key=lambda x: x['name'])
            arquivo_para_remover = csvs_ordenados[0]['name']
            try:
                supabase.storage.from_(SUPABASE_BUCKET).remove([arquivo_para_remover])
                print(f"FIFO: Arquivo removido do bucket: {arquivo_para_remover}")
                arquivos_processados.discard(arquivo_para_remover)
            except Exception as e:
                print(f"Aviso: Nao foi possivel remover arquivo: {e}")
    except Exception as e:
        print(f"Erro ao gerenciar FIFO: {e}")
