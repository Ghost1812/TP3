import os

SUPABASE_DB_URL = os.getenv("SUPABASE_DB_URL", "")
SOCKET_PORT = int(os.getenv("SOCKET_PORT", "8888"))
GRPC_PORT = int(os.getenv("GRPC_PORT", "5000"))
