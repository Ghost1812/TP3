import csv
import io
import time
import re
from typing import Dict, List
from config import MAPPER
from api_client import consultar_api_externa


def processar_csv_stream(csv_bytes: bytes) -> List[Dict]:
    """
    Processa um ficheiro CSV em memória e enriquece os dados com uma API externa.
    """
    # Lista onde serão guardados os dados finais processados
    dados_processados = []

    # Converte os bytes do CSV para um stream de texto
    csv_io = io.TextIOWrapper(
        io.BytesIO(csv_bytes),
        encoding='utf-8-sig',
        newline=''
    )

    # Lê o CSV como dicionários (chave = nome da coluna)
    reader = csv.DictReader(csv_io)

    # Processa cada linha do CSV
    for row in reader:
        dado_mapeado = {}

        # Aplica o mapeamento CSV -> XML
        for csv_key, xml_key in MAPPER.items():
            if csv_key in row:
                dado_mapeado[xml_key] = row[csv_key]

        # Obtém o nome do país a partir dos dados mapeados
        pais = dado_mapeado.get("Nome", "").replace("_", " ").strip()

        # Caso o nome não esteja disponível, tenta extrair a partir do ID interno
        if not pais or len(pais) < 3:
            id_interno = dado_mapeado.get("IDInterno", "")
            match = re.match(r'CSV_([A-Z_]+)_\d+', id_interno)
            if match:
                pais = match.group(1).replace("_", " ").strip()

        # Consulta a API externa para enriquecer os dados
        dados_api = consultar_api_externa(pais)

        # Pequena pausa para evitar excesso de pedidos à API
        if len(dados_processados) % 10 == 0:
            time.sleep(0.1)

        # Combina os dados do CSV com os dados enriquecidos
        dado_final = {
            **dado_mapeado,
            "Media30d": dados_api.get("media_30d", 0),
            "Maximo6m": dados_api.get("maximo_6m", 0),
            "Capital": dados_api.get("capital", "N/A"),
            "Subregiao": dados_api.get("subregion", "N/A"),
            "Moeda": dados_api.get("currency", "N/A"),
            "DensidadePopulacao": dados_api.get("density", 0)
        }

        # Adiciona o registo processado à lista final
        dados_processados.append(dado_final)

    # Devolve a lista de dados processados e enriquecidos
    return dados_processados
