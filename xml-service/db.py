import psycopg2
from config import SUPABASE_DB_URL

def get_db_connection():
    """
    Cria conexao com Supabase Database (PostgreSQL)
    """
    if not SUPABASE_DB_URL:
        raise ValueError("SUPABASE_DB_URL deve estar configurado")

    # Nao trocar portas, nao adicionar pgbouncer
    # A string ja tem sslmode=require
    conn_string = SUPABASE_DB_URL.strip().strip('"').strip("'")

    return psycopg2.connect(conn_string)

def persistir_xml(xml_string: str, mapper_version: str, id_requisicao: str):
    """
    Persiste XML no banco de dados Supabase
    Retorna tupla (sucesso: bool, documento_id: int, status: str)
    """
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
