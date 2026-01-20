"""
XML Service - TP3
Inicia servidores Socket e gRPC para processar e consultar XMLs
"""
import subprocess
import sys
import threading

# Gera arquivos Python a partir do proto se nao existirem
try:
    import xml_service_pb2
except ImportError:
    print("Gerando arquivos Python a partir do proto...")
    subprocess.run([
        sys.executable, "-m", "grpc_tools.protoc",
        "-I.", "--python_out=.", "--grpc_python_out=.", "xml_service.proto"
    ], check=True)
    import xml_service_pb2

from config import SOCKET_PORT, GRPC_PORT
from socket_server import servidor_socket
from grpc_server import servidor_grpc

def main():
    """
    Funcao principal
    Inicia servidor Socket em thread separada e servidor gRPC no thread principal
    """
    print("=" * 60)
    print("XML SERVICE - TP3")
    print("=" * 60)
    print(f"Supabase Database: Configurado via SUPABASE_DB_URL")
    print(f"Socket: 0.0.0.0:{SOCKET_PORT}")
    print(f"gRPC: 0.0.0.0:{GRPC_PORT}")
    print("=" * 60)
    
    socket_thread = threading.Thread(target=servidor_socket, daemon=True)
    socket_thread.start()
    
    servidor_grpc()

if __name__ == "__main__":
    main()
