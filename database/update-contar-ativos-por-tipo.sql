-- Script para atualizar a função contar_ativos_por_tipo no Supabase
-- Execute este script no Supabase SQL Editor para corrigir a contagem de países únicos
-- Acesse: Supabase Dashboard > SQL Editor > New Query > Cole este código > Run

-- Criar função para contar países por região (tipo)
-- MODIFICADA: Agora conta países únicos usando COUNT(DISTINCT nome_pais)
CREATE OR REPLACE FUNCTION contar_ativos_por_tipo(
    p_data_inicio TIMESTAMP DEFAULT NULL,
    p_data_fim TIMESTAMP DEFAULT NULL
)
RETURNS TABLE(tipo VARCHAR, total BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        x.regiao::VARCHAR as tipo,
        COUNT(DISTINCT x.nome_pais)::BIGINT as total -- Conta países únicos, não registros
    FROM documentos_xml dx,
    XMLTABLE(
        '/RelatorioConformidade/Paises/Pais'
        PASSING dx.xml_documento
        COLUMNS
            regiao VARCHAR PATH 'DadosGeograficos/Continente/text()',
            nome_pais VARCHAR PATH '@Nome' -- Necessário para COUNT(DISTINCT)
    ) x
    WHERE (p_data_inicio IS NULL OR dx.data_criacao >= p_data_inicio)
      AND (p_data_fim IS NULL OR dx.data_criacao <= p_data_fim)
      AND x.regiao IS NOT NULL
      AND x.nome_pais IS NOT NULL -- Filtra países sem nome
    GROUP BY x.regiao;
END;
$$ LANGUAGE plpgsql;
