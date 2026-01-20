# Crawler Service - Java

Crawler Service em Java para fazer scraping do Worldometers e upload para Supabase Storage.

## Pre-requisitos

- **Java 17+** instalado
- **Maven 3.8+** instalado
- **Chrome** instalado no sistema (para Selenium)

## Como Executar

### 1. Compilar o projeto

```bash
cd crawler
mvn clean package
```

Isso criará um JAR executável em `target/crawler-1.0.0.jar`

### 2. Configurar variáveis de ambiente

**IMPORTANTE:** 
- `SUPABASE_URL` deve ser a **URL da API REST** (ex: `https://xxxxx.supabase.co`)
- **NAO** use a string de conexao PostgreSQL (`postgresql://...`)
- Encontre a URL correta em: **Supabase Dashboard > Settings > API > Project URL**

```bash
# Windows PowerShell
$env:SUPABASE_URL = "https://seu-projeto.supabase.co"
$env:SUPABASE_KEY = "sua-chave-anon-key"
$env:SUPABASE_BUCKET = "tp3-data"

# Windows CMD
set SUPABASE_URL=https://seu-projeto.supabase.co
set SUPABASE_KEY=sua-chave-anon-key
set SUPABASE_BUCKET=tp3-data

# Linux/Mac
export SUPABASE_URL=https://seu-projeto.supabase.co
export SUPABASE_KEY=sua-chave-anon-key
export SUPABASE_BUCKET=tp3-data
```

**Ou criar arquivo `.env` na raiz do projeto TP3:**
```
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-chave-anon-key
SUPABASE_BUCKET=tp3-data
```

O script `start-crawler.ps1` carrega automaticamente variáveis do arquivo `.env` se existir.

### 3. Executar

```bash
java -jar target/crawler-1.0.0.jar
```

Ou usar o script `start-local.bat` que compila e executa automaticamente.

## Estrutura

```
crawler/
├── pom.xml                                    # Configuracao Maven
├── src/main/java/com/tp3/crawler/
│   ├── Crawler.java                          # Classe principal
│   ├── Config.java                           # Configuracoes
│   ├── DriverBuilder.java                    # Builder do WebDriver
│   ├── Scraper.java                          # Scraping do Worldometers
│   ├── CountryData.java                      # Modelo de dados
│   ├── CSVUtils.java                         # Utilitarios CSV
│   └── SupabaseUploader.java                 # Upload + FIFO
└── target/                                    # Arquivos compilados
```

## Funcionalidades

- Scraping do Worldometers usando Selenium
- Extracao de dados de paises
- Criacao de arquivos CSV
- Upload para Supabase Storage
- Gerenciamento FIFO (maximo 3 arquivos)
- Agendamento automatico (a cada 1 minuto)

## Notas

- O crawler executa **localmente** (não no Docker)
- Requer Chrome instalado no sistema
- WebDriver Manager baixa automaticamente o ChromeDriver
- CSVs são criados temporariamente e removidos após upload
