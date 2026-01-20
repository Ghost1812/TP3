# Crawler Service - Java

Crawler Service em Java para fazer scraping do Worldometers e upload para Supabase Storage.

## 📋 Pré-requisitos

- **Java 17+** instalado
- **Maven 3.8+** instalado
- **Chrome** instalado no sistema (para Selenium)

## 🚀 Como Executar

### 1. Compilar o projeto

```bash
cd crawler
mvn clean package
```

Isso criará um JAR executável em `target/crawler-1.0.0.jar`

### 2. Configurar variáveis de ambiente

```bash
# Windows
set SUPABASE_URL=https://seu-projeto.supabase.co
set SUPABASE_KEY=sua-chave-supabase
set SUPABASE_BUCKET=tp3-data

# Linux/Mac
export SUPABASE_URL=https://seu-projeto.supabase.co
export SUPABASE_KEY=sua-chave-supabase
export SUPABASE_BUCKET=tp3-data
```

### 3. Executar

```bash
java -jar target/crawler-1.0.0.jar
```

Ou usar o script `start-local.bat` que compila e executa automaticamente.

## 📁 Estrutura

```
crawler/
├── pom.xml                                    # Configuração Maven
├── src/main/java/com/tp3/crawler/
│   ├── Crawler.java                          # Classe principal
│   ├── Config.java                           # Configurações
│   ├── DriverBuilder.java                    # Builder do WebDriver
│   ├── Scraper.java                          # Scraping do Worldometers
│   ├── CountryData.java                      # Modelo de dados
│   ├── CSVUtils.java                         # Utilitários CSV
│   └── SupabaseUploader.java                 # Upload + FIFO
└── target/                                    # Arquivos compilados
```

## 🔧 Funcionalidades

- ✅ Scraping do Worldometers usando Selenium
- ✅ Extração de dados de países
- ✅ Criação de arquivos CSV
- ✅ Upload para Supabase Storage
- ✅ Gerenciamento FIFO (máximo 3 arquivos)
- ✅ Agendamento automático (a cada 1 minuto)

## 📝 Notas

- O crawler executa **localmente** (não no Docker)
- Requer Chrome instalado no sistema
- WebDriver Manager baixa automaticamente o ChromeDriver
- CSVs são criados temporariamente e removidos após upload
