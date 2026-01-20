import csv
import io
import time
import re
from typing import Dict, List
from config import MAPPER
from api_client import consultar_api_externa

def processar_csv_stream(csv_bytes: bytes) -> List[Dict]:
    """Processa CSV em stream"""
    dados_processados = []
    
    csv_io = io.TextIOWrapper(io.BytesIO(csv_bytes), encoding='utf-8-sig', newline='')
    reader = csv.DictReader(csv_io)
    
    for row in reader:
        dado_mapeado = {}
        for csv_key, xml_key in MAPPER.items():
            if csv_key in row:
                dado_mapeado[xml_key] = row[csv_key]
        
        pais = dado_mapeado.get("Nome", "").replace("_", " ").strip()
        if not pais:
            pais = dado_mapeado.get("Ticker", "").replace("_", " ").strip()
        
        if not pais or len(pais) < 3:
            id_interno = dado_mapeado.get("IDInterno", "")
            match = re.match(r'CSV_([A-Z_]+)_\d+', id_interno)
            if match:
                pais = match.group(1).replace("_", " ").strip()
        
        dados_api = consultar_api_externa(pais)
        
        if len(dados_processados) < 3:
            print(f"DEBUG - País: {pais}, API retornou: capital={dados_api.get('capital')}, subregion={dados_api.get('subregion')}, moeda={dados_api.get('currency')}, density={dados_api.get('density')}")
        
        if len(dados_processados) % 10 == 0:
            time.sleep(0.1)
        
        dado_final = {
            **dado_mapeado,
            "Media30d": dados_api.get("media_30d", 0),
            "Maximo6m": dados_api.get("maximo_6m", 0),
            "Capital": dados_api.get("capital", "N/A"),
            "Subregiao": dados_api.get("subregion", "N/A"),
            "Moeda": dados_api.get("currency", "N/A"),
            "DensidadePopulacao": dados_api.get("density", 0)
        }
        
        dados_processados.append(dado_final)
    
    return dados_processados
