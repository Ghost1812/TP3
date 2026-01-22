from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY, SUPABASE_BUCKET, MAX_ARQUIVOS_BUCKET

# Conjunto para guardar os ficheiros já processados
arquivos_processados = set()


def monitorizar_bucket():
    """
    Verifica o bucket do Supabase e devolve os CSV ainda não processados.
    """
    try:
        # Cria o cliente Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Lista os ficheiros existentes no bucket
        arquivos = supabase.storage.from_(SUPABASE_BUCKET).list()

        novos_arquivos = []

        # Filtra apenas ficheiros CSV ainda não processados
        for arquivo in arquivos:
            if arquivo['name'].endswith('.csv') and arquivo['name'] not in arquivos_processados:
                novos_arquivos.append(arquivo['name'])

        return novos_arquivos

    except Exception as e:
        print(f"Erro ao monitorizar bucket: {e}")
        return []


def marcar_processado(nome_arquivo: str):
    """
    Marca um ficheiro CSV como já processado.
    """
    arquivos_processados.add(nome_arquivo)


def gerenciar_fifo():
    """
    Aplica a política FIFO no bucket do Supabase.
    Remove o ficheiro CSV mais antigo quando o limite é atingido.
    """
    try:
        # Cria o cliente Supabase
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

        # Lista os ficheiros do bucket
        arquivos = supabase.storage.from_(SUPABASE_BUCKET).list()
        csvs = [f for f in arquivos if f['name'].endswith('.csv')]

        # Remove o ficheiro mais antigo se o limite for atingido
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
