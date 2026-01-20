-- Script para atualizar as funções SQL para usar apenas o XML mais recente
-- Execute este script no Supabase SQL Editor para aplicar as mudanças

-- Atualizar função consultar_xpath para usar apenas o XML mais recente
-- SEMPRE usa apenas o XML mais recente, ignorando id_requisicao se não corresponder
CREATE OR REPLACE FUNCTION consultar_xpath(
    p_xpath TEXT,
    p_id_requisicao VARCHAR DEFAULT NULL,
    p_data_inicio TIMESTAMP DEFAULT NULL,
    p_data_fim TIMESTAMP DEFAULT NULL
)
RETURNS TABLE(resultado TEXT) AS $$
DECLARE
    v_latest_id INTEGER;
BEGIN
    -- SEMPRE buscar o ID do documento mais recente primeiro
    SELECT id INTO v_latest_id 
    FROM documentos_xml 
    ORDER BY data_criacao DESC, id DESC 
    LIMIT 1;
    
    -- Se não houver documentos, retornar vazio
    IF v_latest_id IS NULL THEN
        RETURN;
    END IF;
    
    -- Executar XPath APENAS no documento mais recente
    -- Se id_requisicao for especificado E corresponder ao mais recente, usar
    -- Caso contrário, ignorar id_requisicao e usar apenas o mais recente
    RETURN QUERY
    SELECT unnest(xpath(p_xpath, xml_documento))::TEXT
    FROM documentos_xml
    WHERE id = v_latest_id
      AND (p_id_requisicao IS NULL OR id_requisicao = p_id_requisicao)
      AND (p_data_inicio IS NULL OR data_criacao >= p_data_inicio)
      AND (p_data_fim IS NULL OR data_criacao <= p_data_fim);
END;
$$ LANGUAGE plpgsql;

-- Atualizar função agregar_ativos para usar apenas o XML mais recente
CREATE OR REPLACE FUNCTION agregar_ativos(
    p_tipo VARCHAR DEFAULT NULL,
    p_data_inicio TIMESTAMP DEFAULT NULL,
    p_data_fim TIMESTAMP DEFAULT NULL
)
RETURNS TABLE(
    ticker VARCHAR,
    tipo VARCHAR,
    preco_atual NUMERIC,
    volume BIGINT,
    media_30d NUMERIC,
    maximo_6m NUMERIC,
    capital VARCHAR,
    subregiao VARCHAR,
    moeda VARCHAR,
    densidade NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        x.nome_pais::VARCHAR as ticker,
        x.regiao::VARCHAR as tipo,
        CASE 
            WHEN x.populacao_milhoes IS NOT NULL AND x.populacao_milhoes != '' 
            THEN (x.populacao_milhoes::TEXT)::NUMERIC 
            ELSE 0 
        END as preco_atual,
        CASE 
            WHEN x.populacao_total IS NOT NULL AND x.populacao_total != '' 
            THEN (x.populacao_total::TEXT)::BIGINT 
            ELSE 0 
        END as volume,
        CASE 
            WHEN x.media_30d IS NOT NULL AND x.media_30d != '' 
            THEN (x.media_30d::TEXT)::NUMERIC 
            ELSE 0 
        END as media_30d,
        CASE 
            WHEN x.maximo_6m IS NOT NULL AND x.maximo_6m != '' 
            THEN (x.maximo_6m::TEXT)::NUMERIC 
            ELSE 0 
        END as maximo_6m,
        COALESCE(x.capital, 'N/A')::VARCHAR as capital,
        COALESCE(x.subregiao, 'N/A')::VARCHAR as subregiao,
        COALESCE(x.moeda, 'N/A')::VARCHAR as moeda,
        CASE 
            WHEN x.densidade IS NOT NULL AND x.densidade != '' 
            THEN (x.densidade::TEXT)::NUMERIC 
            ELSE 0 
        END as densidade
    FROM documentos_xml dx,
    XMLTABLE(
        '/RelatorioConformidade/Paises/Pais'
        PASSING dx.xml_documento
        COLUMNS
            id_interno VARCHAR PATH '@IDInterno',
            nome_pais VARCHAR PATH '@Nome',
            populacao_milhoes VARCHAR PATH 'DetalhesPais/PopulacaoMilhoes/text()',
            populacao_total VARCHAR PATH 'DetalhesPais/PopulacaoTotal/text()',
            regiao VARCHAR PATH 'DadosGeograficos/Continente/text()',
            media_30d VARCHAR PATH 'HistoricoAPI/Media30d/text()',
            maximo_6m VARCHAR PATH 'HistoricoAPI/Maximo6m/text()',
            capital VARCHAR PATH 'DadosGeograficos/Capital/text()',
            subregiao VARCHAR PATH 'DadosGeograficos/Subregiao/text()',
            moeda VARCHAR PATH 'DadosGeograficos/Moeda/text()',
            densidade VARCHAR PATH 'DadosGeograficos/DensidadePopulacao/text()'
    ) x
    WHERE dx.id = (SELECT id FROM documentos_xml ORDER BY data_criacao DESC, id DESC LIMIT 1)
      AND (p_tipo IS NULL OR x.regiao = p_tipo)
      AND (p_data_inicio IS NULL OR dx.data_criacao >= p_data_inicio)
      AND (p_data_fim IS NULL OR dx.data_criacao <= p_data_fim)
    ORDER BY x.nome_pais;
END;
$$ LANGUAGE plpgsql;

-- Atualizar função contar_ativos_por_tipo para usar apenas o XML mais recente
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
    WHERE dx.id = (SELECT id FROM documentos_xml ORDER BY data_criacao DESC, id DESC LIMIT 1)
      AND (p_data_inicio IS NULL OR dx.data_criacao >= p_data_inicio)
      AND (p_data_fim IS NULL OR dx.data_criacao <= p_data_fim)
      AND x.regiao IS NOT NULL
      AND x.nome_pais IS NOT NULL
    GROUP BY x.regiao;
END;
$$ LANGUAGE plpgsql;

-- Atualizar função media_precos_por_tipo para usar apenas o XML mais recente
CREATE OR REPLACE FUNCTION media_precos_por_tipo(
    p_data_inicio TIMESTAMP DEFAULT NULL,
    p_data_fim TIMESTAMP DEFAULT NULL
)
RETURNS TABLE(tipo VARCHAR, media_preco NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        x.regiao::VARCHAR as tipo,
        AVG(
            CASE 
                WHEN x.populacao_total IS NOT NULL AND x.populacao_total != '' 
                THEN (x.populacao_total::TEXT)::NUMERIC 
                ELSE NULL 
            END
        )::NUMERIC as media_preco
    FROM documentos_xml dx,
    XMLTABLE(
        '/RelatorioConformidade/Paises/Pais'
        PASSING dx.xml_documento
        COLUMNS
            regiao VARCHAR PATH 'DadosGeograficos/Continente/text()',
            populacao_total VARCHAR PATH 'DetalhesPais/PopulacaoTotal/text()'
    ) x
    WHERE dx.id = (SELECT id FROM documentos_xml ORDER BY data_criacao DESC, id DESC LIMIT 1)
      AND (p_data_inicio IS NULL OR dx.data_criacao >= p_data_inicio)
      AND (p_data_fim IS NULL OR dx.data_criacao <= p_data_fim)
      AND x.regiao IS NOT NULL
      AND x.populacao_total IS NOT NULL
      AND x.populacao_total != ''
    GROUP BY x.regiao;
END;
$$ LANGUAGE plpgsql;
