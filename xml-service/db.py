import psycopg2
from config import SUPABASE_DB_URL

def get_db_connection():
    """Cria conexão com Supabase Database (PostgreSQL)"""
    if not SUPABASE_DB_URL:
        raise ValueError("SUPABASE_DB_URL deve estar configurado")

    # NÃO trocar portas, NÃO adicionar pgbouncer.
    # A tua string já tem sslmode=require, isso chega.
    conn_string = SUPABASE_DB_URL.strip().strip('"').strip("'")

    return psycopg2.connect(conn_string)

def persistir_xml(xml_string: str, mapper_version: str, id_requisicao: str):
    """Persiste XML no Supabase Database"""
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
