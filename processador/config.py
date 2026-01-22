import os

# URL do Supabase (garante que termina com "/")
SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip('/') + '/'

# Chave de autenticação do Supabase
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")

# Nome do bucket onde os CSV são armazenados
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "tp3-data")

# Host do XML Service
XML_SERVICE_HOST = os.getenv("XML_SERVICE_HOST", "xml-service")

# Porta do XML Service
XML_SERVICE_PORT = int(os.getenv("XML_SERVICE_PORT", "8888"))

# URL do webhook usado para notificações
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://processador:5001/webhook")

# Número máximo de ficheiros CSV no bucket
MAX_ARQUIVOS_BUCKET = 3

# Versão do mapeamento usado na transformação para XML
MAPPER_VERSION = "1.0"

# Mapeamento entre campos do CSV e elementos do XML
MAPPER = {
    "ID_Interno": "IDInterno",
    "Nome_Pais": "Nome",
    "Regiao": "Continente",
    "Populacao_Milhoes": "PopulacaoMilhoes",
    "Populacao_Total": "PopulacaoTotal",
    "Data_Coleta": "DataColeta",
    "Unidade": "Unidade"
}
