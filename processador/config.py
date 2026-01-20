import os

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip('/') + '/'
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "tp3-data")
XML_SERVICE_HOST = os.getenv("XML_SERVICE_HOST", "xml-service")
XML_SERVICE_PORT = int(os.getenv("XML_SERVICE_PORT", "8888"))
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "http://processador:5001/webhook")

MAX_ARQUIVOS_BUCKET = 3

MAPPER_VERSION = "1.0"
MAPPER = {
    "ID_Interno": "IDInterno",
    "Ticker": "Nome",
    "Tipo_Ativo": "Continente",
    "Preco_Atual": "PopulacaoMilhoes",
    "Volume_Negociado": "PopulacaoTotal",
    "Data_Negociacao": "DataNegociacao",
    "Moeda": "Moeda"
}
