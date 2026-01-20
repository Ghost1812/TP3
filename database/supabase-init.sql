-- Script SQL para executar no Supabase Database
-- Acesse: Supabase Dashboard > SQL Editor > New Query
-- Cole este script e execute

-- Criar extensão para suporte XML (já disponível no Supabase)
-- XML support is built-in, no extension needed

-- Criar tabela para armazenar documentos XML
CREATE TABLE IF NOT EXISTS documentos_xml (
    id SERIAL PRIMARY KEY,
    xml_documento XML NOT NULL,
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    mapper_version VARCHAR(50) NOT NULL,
    id_requisicao VARCHAR(255),
    status VARCHAR(50) DEFAULT 'OK',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices para melhor performance nas consultas XPath
CREATE INDEX IF NOT EXISTS idx_data_criacao ON documentos_xml(data_criacao);
CREATE INDEX IF NOT EXISTS idx_id_requisicao ON documentos_xml(id_requisicao);
CREATE INDEX IF NOT EXISTS idx_status ON documentos_xml(status);

-- Criar view de compatibilidade para o nome antigo da tabela
CREATE OR REPLACE VIEW xml_documentos AS SELECT * FROM documentos_xml;

-- Criar função para consultas XPath (usada pelo XML Service)
-- MODIFICADA: SEMPRE usa apenas o XML mais recente (último documento)
-- Ignora id_requisicao se não corresponder ao documento mais recente
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

-- Criar função para agregar dados de países usando XMLTABLE
-- MODIFICADA: Agora usa apenas o XML mais recente (último documento)
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

-- Criar função para contar países por região (tipo)
-- MODIFICADA: Agora conta países únicos usando COUNT(DISTINCT nome_pais) e usa apenas o XML mais recente
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

-- Criar função para média de população por região (tipo)
-- MODIFICADA: Agora usa apenas o XML mais recente (último documento)
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
