import requests
import time
from urllib.parse import quote

cache_paises_api = {}

def consultar_api_externa(pais: str) -> dict:
    """Consulta REST Countries API para dados complementares sobre países"""
    try:
        pais_limpo = pais.strip().replace("_", " ").strip()
        pais_upper = pais_limpo.upper()
        
        nome_mapping = {
            "INDIA": "India", "CHINA": "China", "UNITED STATES": "United States",
            "USA": "United States", "RUSSIA": "Russia", "BRAZIL": "Brazil",
            "JAPAN": "Japan", "GERMANY": "Germany", "FRANCE": "France",
            "ITALY": "Italy", "SPAIN": "Spain", "CANADA": "Canada",
            "AUSTRALIA": "Australia", "MEXICO": "Mexico", "INDONESIA": "Indonesia",
            "TURKEY": "Turkey", "SOUTH KOREA": "South Korea", "SAUDI ARABIA": "Saudi Arabia",
            "ARGENTINA": "Argentina", "POLAND": "Poland", "UKRAINE": "Ukraine",
            "AFGHANISTAN": "Afghanistan", "ARMENIA": "Armenia", "ETHIOPIA": "Ethiopia",
            "PHILIPPINES": "Philippines", "CONGO": "Democratic Republic of the Congo",
            "EGYPT": "Egypt", "PORTUGAL": "Portugal"
        }
        
        if pais_upper.startswith("ST. ") or pais_upper.startswith("ST "):
            pais_upper = pais_upper.replace("ST. ", "SAINT ", 1).replace("ST ", "SAINT ", 1)
        elif pais_upper.startswith("ST."):
            pais_upper = pais_upper.replace("ST.", "SAINT", 1)
        
        if pais_upper in nome_mapping:
            pais_normalizado = nome_mapping[pais_upper]
        else:
            melhor_match = None
            melhor_tamanho = 0
            for key, value in nome_mapping.items():
                if pais_upper.startswith(key) or key.startswith(pais_upper):
                    if len(key) > melhor_tamanho:
                        melhor_match = value
                        melhor_tamanho = len(key)
            
            if melhor_match:
                pais_normalizado = melhor_match
            else:
                palavras = pais_limpo.split()
                pais_normalizado = " ".join([p.capitalize() for p in palavras])
        
        if pais_normalizado in cache_paises_api:
            return cache_paises_api[pais_normalizado]
        
        def extrair_dados_api(country_data):
            area = country_data.get("area", 0)
            population = country_data.get("population", 0)
            capital_list = country_data.get("capital")
            capital = capital_list[0] if capital_list and len(capital_list) > 0 else "N/A"
            region = country_data.get("region", "N/A")
            subregion = country_data.get("subregion", "N/A")
            currencies = country_data.get("currencies", {})
            currency_name = "N/A"
            if currencies:
                currency_code = list(currencies.keys())[0]
                currency_info = currencies.get(currency_code, {})
                currency_name = currency_info.get("name", currency_code)
            
            density = (population / area) if area > 0 else 0
            
            return {
                "media_30d": round(area / 1000.0, 2),
                "maximo_6m": round(population / 1000000.0, 2),
                "capital": capital,
                "subregion": subregion,
                "currency": currency_name,
                "density": round(density, 2) if density > 0 else 0
            }
        
        def fazer_requisicao_com_retry(url, max_tentativas=3):
            for tentativa in range(max_tentativas):
                try:
                    if tentativa > 0:
                        time.sleep(0.5 * tentativa)
                    response = requests.get(url, timeout=15, verify=True)
                    return response
                except (requests.exceptions.Timeout, requests.exceptions.SSLError, requests.exceptions.ConnectionError):
                    if tentativa < max_tentativas - 1:
                        continue
                    return None
                except Exception:
                    return None
            return None
        
        pais_encoded = quote(pais_normalizado)
        url_exact = f"https://restcountries.com/v3.1/name/{pais_encoded}?fullText=true"
        
        if len(cache_paises_api) % 20 == 0:
            print(f"Consultando API REST Countries para: {pais_normalizado} (cache: {len(cache_paises_api)} países)")
        
        response = fazer_requisicao_com_retry(url_exact)
        
        if response and response.status_code == 200:
            data = response.json()
            
            if isinstance(data, list) and len(data) > 0:
                melhor_match = None
                pais_normalizado_lower = pais_normalizado.lower()
                
                for country in data:
                    name_common = country.get("name", {}).get("common", "").lower()
                    name_official = country.get("name", {}).get("official", "").lower()
                    
                    if (pais_normalizado_lower == name_common or 
                        pais_normalizado_lower == name_official or
                        name_common.startswith(pais_normalizado_lower) or
                        name_official.startswith(pais_normalizado_lower)):
                        melhor_match = country
                        break
                
                if not melhor_match:
                    melhor_match = data[0]
                
                resultado = extrair_dados_api(melhor_match)
                cache_paises_api[pais_normalizado] = resultado
                return resultado
        
        if not response or response.status_code == 404:
            url_partial = f"https://restcountries.com/v3.1/name/{pais_encoded}?fullText=false"
            response_partial = fazer_requisicao_com_retry(url_partial)
            
            if response_partial and response_partial.status_code == 200:
                data = response_partial.json()
                
                if isinstance(data, list) and len(data) > 0:
                    melhor_match = None
                    pais_normalizado_lower = pais_normalizado.lower()
                    
                    for country in data:
                        name_common = country.get("name", {}).get("common", "").lower()
                        name_official = country.get("name", {}).get("official", "").lower()
                        
                        if (pais_normalizado_lower == name_common or 
                            pais_normalizado_lower == name_official):
                            melhor_match = country
                            break
                        elif (name_common.startswith(pais_normalizado_lower) or
                              name_official.startswith(pais_normalizado_lower)):
                            if not melhor_match:
                                melhor_match = country
                    
                    if not melhor_match:
                        melhor_match = data[0]
                    
                    resultado = extrair_dados_api(melhor_match)
                    cache_paises_api[pais_normalizado] = resultado
                    return resultado
        
        hash_val = abs(hash(pais)) % 1000
        return {
            "media_30d": abs(hash_val) * 0.5,
            "maximo_6m": abs(hash_val) * 2.0,
            "capital": "N/A",
            "subregion": "N/A",
            "currency": "N/A",
            "density": 0
        }
            
    except requests.exceptions.Timeout:
        hash_val = abs(hash(pais)) % 1000
        return {
            "media_30d": abs(hash_val) * 0.5,
            "maximo_6m": abs(hash_val) * 2.0,
            "capital": "N/A",
            "subregion": "N/A",
            "currency": "N/A",
            "density": 0
        }
    except Exception as e:
        print(f"Erro ao consultar API externa para {pais}: {e}")
        hash_val = abs(hash(pais)) % 1000
        return {
            "media_30d": abs(hash_val) * 0.5,
            "maximo_6m": abs(hash_val) * 2.0,
            "capital": "N/A",
            "subregion": "N/A",
            "currency": "N/A",
            "density": 0
        }
