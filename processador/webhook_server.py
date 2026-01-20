from flask import Flask, request, jsonify
from api_client import cache_paises_api

app = Flask(__name__)

@app.route('/cache/clear', methods=['POST'])
def limpar_cache():
    """
    Endpoint para limpar cache de paises da API REST Countries
    """
    try:
        tamanho_antes = len(cache_paises_api)
        cache_paises_api.clear()
        print(f"Cache limpa: {tamanho_antes} entradas removidas")
        return jsonify({
            "sucesso": True,
            "mensagem": f"Cache limpa com sucesso. {tamanho_antes} entradas removidas."
        }), 200
    except Exception as e:
        print(f"Erro ao limpar cache: {e}")
        return jsonify({"sucesso": False, "erro": str(e)}), 500

@app.route('/cache/stats', methods=['GET'])
def estatisticas_cache():
    """Endpoint para ver estatísticas da cache"""
    return jsonify({
        "sucesso": True,
        "tamanho_cache": len(cache_paises_api),
        "paises_em_cache": list(cache_paises_api.keys())[:10]
    }), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Endpoint de webhook para receber confirmacao do XML Service
    Recebe status de persistencia do XML no banco de dados
    """
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
