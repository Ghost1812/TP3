#!/usr/bin/env python3
import os
from http.server import HTTPServer, BaseHTTPRequestHandler

class CustomHandler(BaseHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        super().end_headers()
    
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.end_headers()
            
            # Ler HTML e substituir variável de ambiente
            with open('index.html', 'r', encoding='utf-8') as f:
                html = f.read()
            
            bi_service_url = os.getenv('BI_SERVICE_URL', 'http://localhost:3000')
            html = html.replace('${BI_SERVICE_URL}', bi_service_url)
            
            self.wfile.write(html.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    port = int(os.getenv('PORT', '8080'))
    server = HTTPServer(('', port), CustomHandler)
    print(f'Servidor rodando na porta {port}')
    print(f'BI_SERVICE_URL: {os.getenv("BI_SERVICE_URL", "http://localhost:3000")}')
    print(f'Acesse: http://localhost:{port}')
    server.serve_forever()
