FROM node:18-alpine

WORKDIR /app

# Configurar npm para evitar travamentos
RUN npm config set registry https://registry.npmjs.org/ && \
    npm config set fetch-timeout 300000 && \
    npm config set fetch-retries 5 && \
    npm config set fetch-retry-mintimeout 20000 && \
    npm config set fetch-retry-maxtimeout 120000

# Copiar arquivos de dependências
COPY bi-service/package.json ./

# Instalar dependências com flags para evitar travamentos
# Usa timeout e retries para conexões lentas
RUN npm install --no-audit --no-fund --loglevel=error --progress=false || \
    (echo "Retrying npm install..." && npm install --no-audit --no-fund --loglevel=error --progress=false)

# Criar diretório proto
RUN mkdir -p proto

# Copiar proto do XML Service
COPY xml-service/xml_service.proto ./proto/

# Copiar código fonte
COPY bi-service/src ./src
COPY bi-service/tsconfig.json ./

# Compilar TypeScript
RUN npm run build

EXPOSE 3000 4000

# Script de entrada que compila e executa
COPY bi-service/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
