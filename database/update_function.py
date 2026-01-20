#!/usr/bin/env python3
"""
Script para atualizar a função contar_ativos_por_tipo no Supabase
Este script corrige a contagem para usar países únicos em vez de registros totais
"""
import sys
import os

# Adicionar o diretório xml-service ao path para importar config e db
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'xml-service'))

from db import get_db_connection

def update_function():
    """Atualiza a função contar_ativos_por_tipo no Supabase"""
    
    sql_update = """
    CREATE OR REPLACE FUNCTION contar_ativos_por_tipo(
        p_data_inicio TIMESTAMP DEFAULT NULL,
        p_data_fim TIMESTAMP DEFAULT NULL
    )
    RETURNS TABLE(tipo VARCHAR, total BIGINT) AS $$
    BEGIN
        RETURN QUERY
        SELECT 
            x.regiao::VARCHAR as tipo,
            COUNT(DISTINCT x.nome_pais)::BIGINT as total
        FROM documentos_xml dx,
        XMLTABLE(
            '/RelatorioConformidade/Paises/Pais'
            PASSING dx.xml_documento
            COLUMNS
                regiao VARCHAR PATH 'DadosGeograficos/Continente/text()',
                nome_pais VARCHAR PATH '@Nome'
        ) x
        WHERE (p_data_inicio IS NULL OR dx.data_criacao >= p_data_inicio)
          AND (p_data_fim IS NULL OR dx.data_criacao <= p_data_fim)
          AND x.regiao IS NOT NULL
          AND x.nome_pais IS NOT NULL
        GROUP BY x.regiao;
    END;
    $$ LANGUAGE plpgsql;
    """
    
    try:
        print("Conectando ao Supabase...")
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("Atualizando função contar_ativos_por_tipo...")
        cursor.execute(sql_update)
        conn.commit()
        
        print("Funcao atualizada com sucesso!")
        print("A funcao agora conta paises unicos em vez de registros totais.")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"ERRO ao atualizar funcao: {str(e)}")
        return False

if __name__ == "__main__":
    # Verifica se SUPABASE_DB_URL esta configurado
    if not os.getenv("SUPABASE_DB_URL"):
        print("ERRO: SUPABASE_DB_URL nao esta configurado!")
        print("Configure a variável de ambiente SUPABASE_DB_URL antes de executar.")
        sys.exit(1)
    
    success = update_function()
    sys.exit(0 if success else 1)
