import requests
import time
from urllib.parse import quote

# Cache para evitar chamadas repetidas à API externa
cache_paises_api = {}


def consultar_api_externa(pais: str) -> dict:
    """
    Consulta a REST Countries API para obter dados adicionais de um país.
    """
    try:
        # Normaliza o nome do país recebido
        pais_limpo = pais.strip().replace("_", " ").strip()
        pais_upper = pais_limpo.upper()

        # Mapeamento de nomes comuns para nomes reconhecidos pela API
        nome_mapping = {
            "INDIA": "India", "CHINA": "China", "UNITED STATES": "United States",
            "USA": "United States", "RUSSIA": "Russia", "BRAZIL": "Brazil",
            "JAPAN": "Japan", "GERMANY": "Germany", "FRANCE": "France",
            "ITALY": "Italy", "SPAIN": "Spain", "CANADA": "Canada",
            "AUSTRALIA": "Australia", "MEXICO": "Mexico", "INDONESIA": "Indonesia",
            "TURKEY": "Turkey", "SOUTH KOREA": "South Korea",
            "SAUDI ARABIA": "Saudi Arabia", "PORTUGAL": "Portugal"
        }

        # Trata abreviações como "St." para "Saint"
        if pais_upper.startswith("ST. ") or pais_upper.startswith("ST "):
            pais_upper = pais_upper.replace("ST. ", "SAINT ", 1).replace("ST ", "SAINT ", 1)
        elif pais_upper.startswith("ST."):
            pais_upper = pais_upper.replace("ST.", "SAINT", 1)

        # Define o nome normalizado a usar na API
        if pais_upper in nome_mapping:
            pais_normalizado = nome_mapping[pais_upper]
        else:
            palavras = pais_limpo.split()
            pais_normalizado = " ".join([p.capitalize() for p in palavras])

        # Verifica se o país já está em cache
        if pais_normalizado in cache_paises_api:
            return cache_paises_api[pais_normalizado]

        # Extrai os dados relevantes do JSON devolvido pela API
        def extrair_dados_api(country_data):
            area = country_data.get("area", 0)
            population = country_data.get("population", 0)

            capital_list = country_data.get("capital")
            capital = capital_list[0] if capital_list else "N/A"

            subregion = country_data.get("subregion", "N/A")

            currencies = country_data.get("currencies", {})
            currency_name = "N/A"
            if currencies:
                currency_name = list(currencies.values())[0].get("name", "N/A")

            density = (population / area) if area > 0 else 0

            return {
                "media_30d": round(area / 1000.0, 2),
                "maximo_6m": round(population / 1_000_000.0, 2),
                "capital": capital,
                "subregion": subregion,
                "currency": currency_name,
                "density": round(density, 2)
            }

        # Faz a chamada HTTP com tentativas em caso de falha
        def fazer_requisicao_com_retry(url, max_tentativas=3):
            for tentativa in range(max_tentativas):
                try:
                    if tentativa > 0:
                        time.sleep(0.5 * tentativa)
                    return requests.get(url, timeout=15)
                except Exception:
                    continue
            return None

        # Codifica o nome do país para URL
        pais_encoded = quote(pais_normalizado)

        # Primeira tentativa com correspondência exata
        url = f"https://restcountries.com/v3.1/name/{pais_encoded}?fullText=true"
        response = fazer_requisicao_com_retry(url)

        if response and response.status_code == 200:
            data = response.json()
            resultado = extrair_dados_api(data[0])
            cache_paises_api[pais_normalizado] = resultado
            return resultado

        # Segunda tentativa com correspondência parcial
        url = f"https://restcountries.com/v3.1/name/{pais_encoded}?fullText=false"
        response = fazer_requisicao_com_retry(url)

        if response and response.status_code == 200:
            data = response.json()
            resultado = extrair_dados_api(data[0])
            cache_paises_api[pais_normalizado] = resultado
            return resultado

        # Valores de fallback caso a API não responda
        return {
            "media_30d": 0,
            "maximo_6m": 0,
            "capital": "N/A",
            "subregion": "N/A",
            "currency": "N/A",
            "density": 0
        }

    except Exception as e:
        # Fallback em caso de erro inesperado
        print(f"Erro ao consultar API externa para {pais}: {e}")
        return {
            "media_30d": 0,
            "maximo_6m": 0,
            "capital": "N/A",
            "subregion": "N/A",
            "currency": "N/A",
            "density": 0
        }
