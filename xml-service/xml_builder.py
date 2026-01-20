import uuid
from datetime import datetime
from typing import Dict, List
from lxml import etree
from lxml.etree import Element, SubElement

def criar_xml(dados: List[Dict], mapper_version: str, id_requisicao: str) -> str:
    """Cria XML a partir dos dados processados"""
    root = Element("RelatorioConformidade")
    root.set("DataGeracao", datetime.now().strftime("%Y-%m-%d"))
    root.set("Versao", mapper_version)
    
    config = SubElement(root, "Configuracao")
    config.set("ValidadoPor", f"XML_Service_{uuid.uuid4().hex[:8]}")
    config.set("Requisitante", f"Processador_{id_requisicao[:8]}")
    
    paises = SubElement(root, "Paises")
    
    for dado in dados:
        pais = SubElement(paises, "Pais")
        pais.set("IDInterno", dado.get("IDInterno", ""))
        pais.set("Nome", dado.get("Nome", dado.get("Ticker", "")))
        
        detalhes_pais = SubElement(pais, "DetalhesPais")
        populacao_milhoes = SubElement(detalhes_pais, "PopulacaoMilhoes")
        populacao_milhoes.text = str(dado.get("PopulacaoMilhoes", dado.get("PrecoAtual", "0")))
        
        populacao_total = SubElement(detalhes_pais, "PopulacaoTotal")
        populacao_total.text = str(dado.get("PopulacaoTotal", dado.get("Volume", "0")))
        
        dados_geograficos = SubElement(pais, "DadosGeograficos")
        continente = SubElement(dados_geograficos, "Continente")
        continente.text = dado.get("Continente", dado.get("Tipo", "Desconhecido"))
        
        subregiao = SubElement(dados_geograficos, "Subregiao")
        subregiao_val = dado.get("Subregiao", "N/A")
        subregiao.text = str(subregiao_val) if subregiao_val and subregiao_val != "N/A" else "N/A"
        
        capital = SubElement(dados_geograficos, "Capital")
        capital_val = dado.get("Capital", "N/A")
        capital.text = str(capital_val) if capital_val and capital_val != "N/A" else "N/A"
        
        moeda = SubElement(dados_geograficos, "Moeda")
        moeda_val = dado.get("Moeda", "N/A")
        moeda.text = str(moeda_val) if moeda_val and moeda_val != "N/A" else "N/A"
        
        densidade = SubElement(dados_geograficos, "DensidadePopulacao")
        densidade_val = dado.get("DensidadePopulacao", 0)
        densidade.text = str(densidade_val) if densidade_val and densidade_val != 0 else "0"
        
        historico = SubElement(pais, "HistoricoAPI")
        media_30d = SubElement(historico, "Media30d")
        media_30d.text = str(dado.get("Media30d", "0"))
        
        maximo_6m = SubElement(historico, "Maximo6m")
        maximo_6m.text = str(dado.get("Maximo6m", "0"))
    
    xml_string = etree.tostring(root, encoding='unicode', pretty_print=True, xml_declaration=False)
    xml_string = '<?xml version="1.0" encoding="UTF-8"?>\n' + xml_string
    return xml_string

def validar_xml(xml_string: str):
    """Valida XML"""
    try:
        etree.fromstring(xml_string.encode('utf-8'))
        return True, "XML válido"
    except etree.XMLSyntaxError as e:
        return False, f"Erro de validação: {str(e)}"
