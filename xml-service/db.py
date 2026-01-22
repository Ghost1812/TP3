import psycopg2
from config import SUPABASE_DB_URL


def get_db_connection():
    """
    Cria e devolve uma ligação à base de dados do Supabase (PostgreSQL).
    """
    # Verifica se a string de ligação está configurada
    if not SUPABASE_DB_URL:
        raise ValueError("SUPABASE_DB_URL deve estar configurado")

    # Limpa a string de ligação (sem alterar portas ou sslmode)
    conn_string = SUPABASE_DB_URL.strip().strip('"').strip("'")

    # Cria a ligação à base de dados
    return psycopg2.connect(conn_string)


def persistir_xml(xml_string: str, mapper_version: str, id_requisicao: str):
    """
    Guarda o documento XML no banco de dados.
    Devolve o estado da operação e o ID gerado.
    """
    try:
        # Abre ligação à base de dados
        conn = get_db_connection()
        cursor = conn.cursor()

        # Insere o XML na tabela
        cursor.execute(
            """
            INSERT INTO documentos_xml (xml_documento, mapper_version, id_requisicao, status)
            VALUES (%s, %s, %s, %s)
            RETURNING id
            """,
            (xml_string, mapper_version, id_requisicao, "OK")
        )

        # Obtém o ID do documento inserido
        documento_id = cursor.fetchone()[0]

        # Confirma a transação
        conn.commit()

        # Fecha a ligação
        cursor.close()
        conn.close()

        return True, documento_id, "OK"

    except Exception as e:
        # Erro ao persistir o XML
        return False, 0, f"ERRO_PERSISTENCIA: {str(e)}"
