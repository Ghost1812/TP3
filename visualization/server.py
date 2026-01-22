#!/usr/bin/env python3
import os
from http.server import HTTPServer, BaseHTTPRequestHandler


class CustomHandler(BaseHTTPRequestHandler):
    """
    Handler HTTP responsável por servir o ficheiro index.html.
    Substitui variáveis de ambiente no HTML antes de o devolver.
    """

    def end_headers(self):
        # Permite pedidos de qualquer origem (CORS)
        self.send_header('Access-Control-Allow-Origin', '*')

        # Define o tipo de conteúdo como HTML
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        super().end_headers()

    def do_GET(self):
        # Serve a página principal
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.end_headers()

            # Lê o ficheiro HTML
            with open('index.html', 'r', encoding='utf-8') as f:
                html = f.read()

            # Substitui a variável BI_SERVICE_URL no HTML
            bi_service_url = os.getenv('BI_SERVICE_URL', 'http://localhost:3000')
            html = html.replace('${BI_SERVICE_URL}', bi_service_url)

            # Envia o HTML para o cliente
            self.wfile.write(html.encode('utf-8'))

        else:
            # Qualquer outro caminho devolve 404
            self.send_response(404)
            self.end_headers()


if __name__ == '__main__':
    """
    Inicia um servidor HTTP simples para a visualização.
    """
    # Porta onde o servidor vai escutar
    port = int(os.getenv('PORT', '8080'))

    # Cria e inicia o servidor HTTP
    server = HTTPServer(('', port), CustomHandler)

    print(f'Servidor rodando na porta {port}')
    print(f'BI_SERVICE_URL: {os.getenv("BI_SERVICE_URL", "http://localhost:3000")}')
    print(f'Acesse: http://localhost:{port}')

    server.serve_forever()
