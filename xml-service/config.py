import os

# String de ligação à base de dados do Supabase (PostgreSQL)
SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL", "")

# Porta usada pelo serviço de sockets TCP
SOCKET_PORT = int(os.getenv("SOCKET_PORT", "8888"))

# Porta usada pelo serviço gRPC
GRPC_PORT = int(os.getenv("GRPC_PORT", "5000"))
