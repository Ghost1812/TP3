FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar arquivo proto e gerar codigo Python
COPY xml_service.proto .
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. xml_service.proto

# Copiar schema XSD para validacao
COPY xml_schema.xsd .

# Copiar todos os arquivos Python necessarios
COPY config.py .
COPY db.py .
COPY xml_builder.py .
COPY socket_server.py .
COPY grpc_server.py .
COPY main.py .

EXPOSE 8888 5000

CMD ["python", "main.py"]
