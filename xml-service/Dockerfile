FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY xml_service.proto .
COPY main.py .

# Gerar arquivos Python a partir do proto em runtime se não existirem
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. xml_service.proto || true

EXPOSE 8888 5000

CMD ["python", "main.py"]
