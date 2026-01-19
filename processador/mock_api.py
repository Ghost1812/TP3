"""
Mock API Externa - Para testes locais
Execute: python mock_api.py
"""
from flask import Flask, jsonify

app = Flask(__name__)

# Dados simulados por ticker
DADOS_MOCK = {
    "AAPL": {"media_30d": 145.0, "maximo_6m": 160.0},
    "GOOGL": {"media_30d": 135.0, "maximo_6m": 150.0},
    "MSFT": {"media_30d": 380.0, "maximo_6m": 400.0},
    "AMZN": {"media_30d": 150.0, "maximo_6m": 170.0},
    "TSLA": {"media_30d": 250.0, "maximo_6m": 300.0},
    "META": {"media_30d": 320.0, "maximo_6m": 350.0},
    "NVDA": {"media_30d": 500.0, "maximo_6m": 550.0},
    "NFLX": {"media_30d": 450.0, "maximo_6m": 480.0},
    "AMD": {"media_30d": 120.0, "maximo_6m": 140.0},
    "INTC": {"media_30d": 45.0, "maximo_6m": 50.0},
}

@app.route('/v1/stocks/<ticker>', methods=['GET'])
def get_stock_data(ticker):
    """Retorna dados simulados para um ticker"""
    ticker_upper = ticker.upper()
    
    if ticker_upper in DADOS_MOCK:
        return jsonify(DADOS_MOCK[ticker_upper])
    else:
        # Retorna valores padrão para tickers desconhecidos
        return jsonify({
            "media_30d": 100.0,
            "maximo_6m": 120.0
        })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "OK"})

if __name__ == '__main__':
    print("Mock API Externa rodando em http://localhost:5002")
    print("Configure API_EXTERNA_URL=http://localhost:5002 no .env")
    app.run(host='0.0.0.0', port=5002, debug=True)
