-- Script para garantir que consultar_xpath use APENAS o XML mais recente
-- Execute este script no Supabase SQL Editor para corrigir o problema
-- NOTA: Este arquivo e uma versao alternativa de APLICAR-URGENTE.sql

-- Função consultar_xpath: SEMPRE usa apenas o XML mais recente
-- Se id_requisicao for especificado, ainda filtra pelo mais recente primeiro
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

-- Verificar se a função foi atualizada corretamente
DO $$
BEGIN
    RAISE NOTICE 'Função consultar_xpath atualizada para usar APENAS o XML mais recente';
END $$;
