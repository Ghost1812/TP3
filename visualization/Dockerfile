FROM python:3.11-slim

WORKDIR /app

COPY index.html .
COPY server.py .

EXPOSE 8080

ENV PORT=8080

CMD ["python", "server.py"]
