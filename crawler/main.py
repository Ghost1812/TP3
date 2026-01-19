"""
Crawler Service - TP3
Faz scraping do Worldometers e faz upload para Supabase Storage
"""
import os
import csv
import time
import schedule
import re
from datetime import datetime
from supabase import create_client, Client
from typing import List, Dict
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

# Configuração Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "market-data")

# URL do site para fazer crawl
WORLDMETERS_URL = "https://www.worldometers.info/geography/countries-of-the-world/"

def build_driver(headless: bool = True):
    """Cria driver do Selenium"""
    opts = Options()
    opts.page_load_strategy = "eager"
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--lang=en-US")
    opts.add_argument("--window-size=1920,1080")
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    )
    
    driver_path = ChromeDriverManager().install()
    driver = webdriver.Chrome(service=Service(driver_path), options=opts)
    driver.set_page_load_timeout(30)
    return driver

def extrair_dados_paises() -> List[Dict]:
    """Faz scraping da tabela de países do Worldometers"""
    dados = []
    driver = None
    
    try:
        print("Conectando ao Worldometers...")
        driver = build_driver(headless=True)
        driver.get(WORLDMETERS_URL)
        
        # Aguardar tabela carregar
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        
        time.sleep(2)  # Aguardar renderização completa
        
        # Usar BeautifulSoup para parsear HTML
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Encontrar todas as tabelas
        tabelas = soup.find_all('table')
        
        if not tabelas:
            print("Nenhuma tabela encontrada")
            return dados
        
        # Processar primeira tabela (países principais)
        tabela = tabelas[0]
        linhas = tabela.find_all('tr')
        
        print(f"Processando {len(linhas)} linhas da tabela...")
        
        for idx, linha in enumerate(linhas[1:], start=1):  # Pular cabeçalho
            colunas = linha.find_all(['td', 'th'])
            
            if len(colunas) >= 3:
                try:
                    # Extrair dados das colunas
                    rank = colunas[0].get_text(strip=True)
                    pais_link = colunas[1].find('a')
                    pais = pais_link.get_text(strip=True) if pais_link else colunas[1].get_text(strip=True)
                    populacao_str = colunas[2].get_text(strip=True)
                    regiao_link = colunas[3].find('a') if len(colunas) > 3 else None
                    regiao = regiao_link.get_text(strip=True) if regiao_link else (colunas[3].get_text(strip=True) if len(colunas) > 3 else "")
                    
                    # Limpar população (remover vírgulas)
                    populacao = int(re.sub(r'[,\s]', '', populacao_str)) if populacao_str else 0
                    
                    # Criar ID interno baseado no país
                    id_interno_base = f"CSV_{pais.upper().replace(' ', '_')[:20]}_{idx:03d}"
                    
                    # Multiplicar dados por 10 (criar 10 registros para cada país)
                    for multiplicador in range(10):
                        dados.append({
                            "ID_Interno": f"{id_interno_base}_{multiplicador:02d}",
                            "Ticker": pais[:10].upper().replace(' ', '_'),  # Usar nome do país como "ticker"
                            "Tipo_Ativo": regiao if regiao else "Desconhecido",
                            "Preco_Atual": populacao / 1000000.0,  # Converter população para milhões
                            "Volume_Negociado": populacao,
                            "Data_Negociacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "Moeda": "Pessoas"
                        })
                    
                except Exception as e:
                    print(f"Erro ao processar linha {idx}: {e}")
                    continue
        
        print(f"Extraidos {len(dados)} registros (multiplicados por 10)")
        
    except Exception as e:
        print(f"Erro ao fazer scraping: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if driver:
            driver.quit()
    
    return dados

def criar_csv_temporario(dados: List[Dict]) -> str:
    """Cria arquivo CSV temporário"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"market_data_{timestamp}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        if dados:
            writer = csv.DictWriter(f, fieldnames=dados[0].keys())
            writer.writeheader()
            writer.writerows(dados)
    
    return filename

def gerenciar_fifo_bucket(supabase: Client, novo_arquivo: str):
    """Implementa FIFO: mantém máximo 3 CSVs no bucket, apaga o mais antigo"""
    try:
        # Listar todos os arquivos CSV no bucket
        arquivos = supabase.storage.from_(SUPABASE_BUCKET).list()
        
        # Filtrar apenas CSVs
        csvs = [f for f in arquivos if f['name'].endswith('.csv')]
        
        # Se já tem 3 ou mais CSVs, ordenar por nome (timestamp) e apagar o mais antigo
        if len(csvs) >= 3:
            # Ordenar por nome (que contém timestamp) - mais antigo primeiro
            csvs_ordenados = sorted(csvs, key=lambda x: x['name'])
            
            # Apagar o mais antigo (primeiro da lista)
            arquivo_antigo = csvs_ordenados[0]['name']
            try:
                supabase.storage.from_(SUPABASE_BUCKET).remove([arquivo_antigo])
                print(f"Arquivo mais antigo removido (FIFO): {arquivo_antigo}")
            except Exception as e:
                print(f"Erro ao remover arquivo antigo: {e}")
        
    except Exception as e:
        print(f"Erro ao gerenciar FIFO: {e}")

def upload_para_supabase(filename: str) -> bool:
    """Faz upload do CSV para Supabase Storage com FIFO"""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Gerenciar FIFO antes de fazer upload
        gerenciar_fifo_bucket(supabase, filename)
        
        with open(filename, 'rb') as f:
            file_data = f.read()
        
        # Upload para o bucket
        response = supabase.storage.from_(SUPABASE_BUCKET).upload(
            filename,
            file_data,
            file_options={"content-type": "text/csv", "upsert": "true"}
        )
        
        print(f"CSV enviado para Supabase: {filename}")
        
        # Remove arquivo local após upload
        os.remove(filename)
        
        return True
    except Exception as e:
        print(f"Erro ao fazer upload: {e}")
        return False

def job_gerar_e_enviar():
    """Job agendado para fazer scraping e enviar CSV"""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Iniciando scraping...")
    
    dados = extrair_dados_paises()
    
    if not dados:
        print("Nenhum dado extraido")
        return
    
    print(f"Extraidos {len(dados)} registros")
    
    filename = criar_csv_temporario(dados)
    print(f"CSV criado: {filename}")
    
    if upload_para_supabase(filename):
        print("Processo concluido com sucesso")
    else:
        print("Falha no processo")

def main():
    """Função principal"""
    print("=" * 60)
    print("CRAWLER SERVICE - TP3")
    print("=" * 60)
    print(f"Supabase URL: {SUPABASE_URL}")
    print(f"Bucket: {SUPABASE_BUCKET}")
    print("=" * 60)
    
    # Verificar configuração
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Erro: SUPABASE_URL e SUPABASE_KEY devem estar configurados")
        return
    
    # Executar imediatamente uma vez
    print("\n[INICIAL] Executando primeiro scraping...")
    job_gerar_e_enviar()
    
    # Agendar execução periódica (a cada 2 minutos)
    schedule.every(2).minutes.do(job_gerar_e_enviar)
    
    print("\nAgendado para executar a cada 2 minutos")
    print("Maximo de 3 CSVs no bucket (FIFO)")
    print("Pressione Ctrl+C para parar\n")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nCrawler interrompido pelo usuario")

if __name__ == "__main__":
    main()
