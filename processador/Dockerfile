FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todos os arquivos Python necessarios
COPY config.py .
COPY api_client.py .
COPY bucket_monitor.py .
COPY csv_processor.py .
COPY socket_client.py .
COPY webhook_server.py .
COPY main.py .

EXPOSE 5001

CMD ["python", "main.py"]
