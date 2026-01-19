"""
Processador Service - TP3
Monitoriza bucket Supabase, processa CSV, consome API externa e envia para XML Service via Socket
"""
import os
import csv
import io
import socket
import json
import time
import requests
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from supabase import create_client, Client
from flask import Flask, request, jsonify

app = Flask(__name__)

# Configuração
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "market-data")
XML_SERVICE_HOST = os.getenv("XML_SERVICE_HOST", "xml-service")
XML_SERVICE_PORT = int(os.getenv("XML_SERVICE_PORT", "8888"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://processador:5001/webhook")
API_EXTERNA_URL = os.getenv("API_EXTERNA_URL", "https://api.exemplo.com/v1/stocks")

# Mapeamento de atributos CSV para XML (desacoplamento)
MAPPER_VERSION = "1.0"
MAPPER = {
    "ID_Interno": "IDInterno",
    "Ticker": "Nome",  # Nome do país
    "Tipo_Ativo": "Continente",  # Continente/Região
    "Preco_Atual": "PopulacaoMilhoes",  # População em milhões
    "Volume_Negociado": "PopulacaoTotal",  # População total
    "Data_Negociacao": "DataNegociacao",
    "Moeda": "Moeda"
}

# Cache de arquivos processados
arquivos_processados = set()

def consultar_api_externa(pais: str) -> Dict:
    """Consulta REST Countries API para dados complementares sobre países"""
    try:
        # Normalizar nome do país para busca
        # Remover underscores e espaços extras, capitalizar primeira letra
        pais_limpo = pais.strip().replace("_", " ").title()
        
        # Mapeamento de nomes comuns que podem estar truncados ou em formato diferente
        nome_mapping = {
            "INDIA": "India",
            "CHINA": "China",
            "UNITED STATES": "United States",
            "UNITED": "United States of America",  # Nome completo para evitar confusão
            "RUSSIA": "Russia",
            "BRAZIL": "Brazil",
            "JAPAN": "Japan",
            "GERMANY": "Germany",
            "FRANCE": "France",
            "ITALY": "Italy",
            "SPAIN": "Spain",
            "CANADA": "Canada",
            "AUSTRALIA": "Australia",
            "MEXICO": "Mexico",
            "INDONESIA": "Indonesia",
            "TURKEY": "Turkey",
            "SOUTH KOREA": "South Korea",
            "SOUTH": "South Korea",
            "SAUDI ARABIA": "Saudi Arabia",
            "SAUDI": "Saudi Arabia",
            "ARGENTINA": "Argentina",
            "POLAND": "Poland",
            "UKRAINE": "Ukraine"
        }
        
        # Verificar se o nome está no mapeamento (busca exata primeiro)
        pais_upper = pais_limpo.upper()
        if pais_upper in nome_mapping:
            pais_normalizado = nome_mapping[pais_upper]
        else:
            # Tentar busca parcial
            for key, value in nome_mapping.items():
                if pais_upper.startswith(key) and len(key) >= 4:  # Mínimo 4 caracteres para evitar falsos positivos
                    pais_normalizado = value
                    break
            else:
                pais_normalizado = pais_limpo
        
        # Tentar buscar por nome completo primeiro
        from urllib.parse import quote
        pais_encoded = quote(pais_normalizado)
        url = f"https://restcountries.com/v3.1/name/{pais_encoded}"
        print(f"Consultando API REST Countries para: {pais_normalizado}")
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Se retornar lista, pegar primeiro resultado
            if isinstance(data, list) and len(data) > 0:
                country_data = data[0]
            else:
                country_data = data
            
            # Extrair dados úteis
            area = country_data.get("area", 0)  # Área em km²
            population = country_data.get("population", 0)
            capital = country_data.get("capital", ["N/A"])[0] if country_data.get("capital") else "N/A"
            region = country_data.get("region", "N/A")
            subregion = country_data.get("subregion", "N/A")
            currencies = country_data.get("currencies", {})
            currency_name = list(currencies.keys())[0] if currencies else "N/A"
            
            # Calcular densidade populacional (habitantes/km²)
            density = (population / area) if area > 0 else 0
            
            resultado = {
                "media_30d": round(area / 1000.0, 2),  # Área em milhares de km²
                "maximo_6m": round(population / 1000000.0, 2),  # População em milhões
                "capital": capital,
                "subregion": subregion,
                "currency": currency_name,
                "density": round(density, 2) if density > 0 else 0
            }
            
            # Debug: imprimir resultado para alguns países
            if pais_normalizado in ["India", "China", "United States", "Brazil"]:
                print(f"DEBUG API - {pais_normalizado}: capital={capital}, subregion={subregion}, currency={currency_name}, density={resultado['density']}")
            
            return resultado
        else:
            # Se não encontrar, tentar busca parcial
            from urllib.parse import quote
            pais_encoded = quote(pais_normalizado)
            url_partial = f"https://restcountries.com/v3.1/name/{pais_encoded}?fullText=false"
            response_partial = requests.get(url_partial, timeout=5)
            
            if response_partial.status_code == 200:
                data = response_partial.json()
                if isinstance(data, list) and len(data) > 0:
                    country_data = data[0]
                    area = country_data.get("area", 0)
                    population = country_data.get("population", 0)
                    capital = country_data.get("capital", ["N/A"])[0] if country_data.get("capital") else "N/A"
                    subregion = country_data.get("subregion", "N/A")
                    currencies = country_data.get("currencies", {})
                    currency_name = list(currencies.keys())[0] if currencies else "N/A"
                    density = (population / area) if area > 0 else 0
                    
                    return {
                        "media_30d": round(area / 1000.0, 2),
                        "maximo_6m": round(population / 1000000.0, 2),
                        "capital": capital,
                        "subregion": subregion,
                        "currency": currency_name,
                        "density": round(density, 2) if density > 0 else 0
                    }
            
            # Fallback: dados simulados baseados no hash do nome
            print(f"País não encontrado na API: {pais_normalizado}, usando dados simulados")
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
        print(f"Timeout ao consultar API para {pais}")
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

def processar_csv_stream(csv_bytes: bytes) -> List[Dict]:
    """Processa CSV em stream"""
    dados_processados = []
    
    csv_io = io.TextIOWrapper(io.BytesIO(csv_bytes), encoding='utf-8-sig', newline='')
    reader = csv.DictReader(csv_io)
    
    for row in reader:
        # Aplicar mapper (desacoplamento de nomes)
        dado_mapeado = {}
        for csv_key, xml_key in MAPPER.items():
            if csv_key in row:
                dado_mapeado[xml_key] = row[csv_key]
        
        # Consultar API externa para enriquecer dados
        # O "Nome" contém o nome do país (mapeado do Ticker)
        pais = dado_mapeado.get("Nome", "").replace("_", " ").strip()
        if not pais:
            # Fallback para Ticker se Nome não existir
            pais = dado_mapeado.get("Ticker", "").replace("_", " ").strip()
        
        # Se ainda não tiver nome, tentar extrair do IDInterno
        if not pais or len(pais) < 3:
            import re
            id_interno = dado_mapeado.get("IDInterno", "")
            # Tentar extrair nome do IDInterno (formato: CSV_COUNTRYNAME_XXX_YY)
            match = re.match(r'CSV_([A-Z_]+)_\d+', id_interno)
            if match:
                pais = match.group(1).replace("_", " ").strip()
        
        dados_api = consultar_api_externa(pais)
        
        # Debug: imprimir alguns resultados
        if len(dados_processados) < 3:
            print(f"DEBUG - País: {pais}, API retornou: capital={dados_api.get('capital')}, subregion={dados_api.get('subregion')}, moeda={dados_api.get('currency')}, density={dados_api.get('density')}")
        
        # Combinar dados CSV + API Externa
        dado_final = {
            **dado_mapeado,
            "Media30d": dados_api.get("media_30d", 0),
            "Maximo6m": dados_api.get("maximo_6m", 0),
            # Novos campos opcionais da API
            "Capital": dados_api.get("capital", "N/A"),
            "Subregiao": dados_api.get("subregion", "N/A"),
            "Moeda": dados_api.get("currency", "N/A"),
            "DensidadePopulacao": dados_api.get("density", 0)
        }
        
        dados_processados.append(dado_final)
    
    return dados_processados

def enviar_para_xml_service(id_requisicao: str, mapper: Dict, webhook_url: str, dados: List[Dict]) -> bool:
    """Envia dados para XML Service via Socket"""
    try:
        # Criar mensagem JSON
        mensagem = {
            "id_requisicao": id_requisicao,
            "mapper": mapper,
            "mapper_version": MAPPER_VERSION,
            "webhook_url": webhook_url,
            "dados": dados
        }
        
        mensagem_json = json.dumps(mensagem)
        mensagem_bytes = mensagem_json.encode('utf-8')
        
        # Conectar ao XML Service via Socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(30)
        
        print(f"Conectando ao XML Service em {XML_SERVICE_HOST}:{XML_SERVICE_PORT}...")
        sock.connect((XML_SERVICE_HOST, XML_SERVICE_PORT))
        
        # Enviar tamanho da mensagem primeiro (4 bytes)
        tamanho = len(mensagem_bytes)
        sock.sendall(tamanho.to_bytes(4, byteorder='big'))
        
        # Enviar mensagem
        sock.sendall(mensagem_bytes)
        
        # Receber confirmação
        resposta_tamanho = int.from_bytes(sock.recv(4), byteorder='big')
        resposta_bytes = sock.recv(resposta_tamanho)
        resposta = json.loads(resposta_bytes.decode('utf-8'))
        
        sock.close()
        
        if resposta.get("status") == "OK":
            print(f"Dados enviados com sucesso. ID Requisicao: {id_requisicao}")
            return True
        else:
            print(f"Erro ao enviar dados: {resposta.get('erro', 'Erro desconhecido')}")
            return False
            
    except Exception as e:
        print(f"Erro ao conectar ao XML Service: {e}")
        return False

def monitorizar_bucket():
    """Monitoriza bucket do Supabase por novos arquivos"""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Listar arquivos no bucket
        arquivos = supabase.storage.from_(SUPABASE_BUCKET).list()
        
        novos_arquivos = []
        for arquivo in arquivos:
            if arquivo['name'].endswith('.csv') and arquivo['name'] not in arquivos_processados:
                novos_arquivos.append(arquivo['name'])
        
        return novos_arquivos
    except Exception as e:
        print(f"Erro ao monitorizar bucket: {e}")
        return []

def processar_arquivo(nome_arquivo: str):
    """Processa um arquivo CSV do bucket"""
    try:
        print(f"\nProcessando arquivo: {nome_arquivo}")
        
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Baixar arquivo do bucket
        csv_bytes = supabase.storage.from_(SUPABASE_BUCKET).download(nome_arquivo)
        
        print(f"Arquivo baixado: {len(csv_bytes)} bytes")
        
        # Processar CSV em stream
        dados_processados = processar_csv_stream(csv_bytes)
        print(f"Processados {len(dados_processados)} registros")
        
        # Gerar ID de requisição
        id_requisicao = str(uuid.uuid4())
        
        # Enviar para XML Service
        sucesso = enviar_para_xml_service(
            id_requisicao=id_requisicao,
            mapper=MAPPER,
            webhook_url=WEBHOOK_URL,
            dados=dados_processados
        )
        
        if sucesso:
            # Marcar arquivo como processado
            arquivos_processados.add(nome_arquivo)
            
            # Apagar CSV do bucket após confirmação
            try:
                supabase.storage.from_(SUPABASE_BUCKET).remove([nome_arquivo])
                print(f"Arquivo removido do bucket: {nome_arquivo}")
            except Exception as e:
                print(f"Aviso: Nao foi possivel remover arquivo: {e}")
        else:
            print(f"Falha ao processar arquivo: {nome_arquivo}")
            
    except Exception as e:
        print(f"Erro ao processar arquivo {nome_arquivo}: {e}")
        import traceback
        traceback.print_exc()

@app.route('/webhook', methods=['POST'])
def webhook():
    """Endpoint de webhook para receber confirmação do XML Service"""
    try:
        dados = request.get_json()
        
        id_requisicao = dados.get('id_requisicao')
        status = dados.get('status')
        documento_id = dados.get('documento_id')
        
        print(f"\nWebhook recebido:")
        print(f"   ID Requisicao: {id_requisicao}")
        print(f"   Status: {status}")
        print(f"   Documento ID: {documento_id}")
        
        if status == "OK":
            print("XML salvo com sucesso!")
        elif status == "ERRO_VALIDACAO":
            print("Erro na validacao do XML")
        elif status == "ERRO_PERSISTENCIA":
            print("Erro ao persistir XML no banco")
        
        return jsonify({"status": "received"}), 200
        
    except Exception as e:
        print(f"Erro ao processar webhook: {e}")
        return jsonify({"erro": str(e)}), 500

def loop_monitoramento():
    """Loop principal de monitoramento"""
    print("=" * 60)
    print("PROCESSADOR SERVICE - TP3")
    print("=" * 60)
    print(f"Supabase Bucket: {SUPABASE_BUCKET}")
    print(f"XML Service: {XML_SERVICE_HOST}:{XML_SERVICE_PORT}")
    print(f"Webhook URL: {WEBHOOK_URL}")
    print("=" * 60)
    
    while True:
        try:
            novos_arquivos = monitorizar_bucket()
            
            if novos_arquivos:
                print(f"\nEncontrados {len(novos_arquivos)} novo(s) arquivo(s)")
                for arquivo in novos_arquivos:
                    processar_arquivo(arquivo)
            else:
                print(".", end="", flush=True)
            
            time.sleep(10)  # Verificar a cada 10 segundos
            
        except KeyboardInterrupt:
            print("\n\nProcessador interrompido pelo usuario")
            break
        except Exception as e:
            print(f"\nErro no loop de monitoramento: {e}")
            time.sleep(10)

if __name__ == "__main__":
    import threading
    
    # Iniciar servidor Flask em thread separada
    flask_thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=5001, debug=False), daemon=True)
    flask_thread.start()
    
    # Iniciar loop de monitoramento
    loop_monitoramento()
