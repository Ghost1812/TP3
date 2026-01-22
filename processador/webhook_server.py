from flask import Flask, request, jsonify
from api_client import cache_paises_api

# Cria a aplicação Flask
app = Flask(__name__)


@app.route('/cache/clear', methods=['POST'])
def limpar_cache():
    """
    Limpa a cache utilizada nas consultas à API externa.
    """
    try:
        # Guarda o tamanho da cache antes da limpeza
        tamanho_antes = len(cache_paises_api)

        # Limpa a cache
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
    """
    Devolve estatísticas básicas da cache.
    """
    return jsonify({
        "sucesso": True,
        "tamanho_cache": len(cache_paises_api),
        "paises_em_cache": list(cache_paises_api.keys())[:10]
    }), 200


@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Recebe notificações do XML Service sobre o estado da persistência.
    """
    try:
        # Lê os dados enviados pelo XML Service
        dados = request.get_json()

        id_requisicao = dados.get('id_requisicao')
        status = dados.get('status')
        documento_id = dados.get('documento_id')

        # Mostra o resultado recebido
        print(f"\nWebhook recebido:")
        print(f"   ID Requisicao: {id_requisicao}")
        print(f"   Status: {status}")
        print(f"   Documento ID: {documento_id}")

        # Interpreta o estado devolvido pelo XML Service
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
