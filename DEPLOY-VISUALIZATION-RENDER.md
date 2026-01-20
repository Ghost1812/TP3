# Deploy da Visualização no Render

## Passo 1: Criar conta no Render

1. Acesse: https://render.com
2. Crie uma conta (pode usar GitHub)

## Passo 2: Criar novo Web Service

1. No dashboard do Render, clique em **New +** > **Web Service**
2. Conecte seu repositório GitHub (ou faça upload do código)
3. Configure:
   - **Name**: `visualization`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt` (ou deixe vazio)
   - **Start Command**: `python server.py`
   - **Root Directory**: `visualization`

## Passo 3: Configurar Variáveis de Ambiente

No Render Dashboard > Environment:
- `PORT`: `8080` (ou deixe vazio, Render define automaticamente)
- `BI_SERVICE_URL`: `https://seu-bi-service-url.onrender.com` (URL do seu BI Service no Render)

## Passo 4: Deploy

1. Clique em **Create Web Service**
2. Render vai fazer build e deploy automaticamente
3. Aguarde alguns minutos

## Passo 5: Obter URL

Após o deploy, você terá uma URL tipo:
`https://visualization-xxxx.onrender.com`

## Alternativa: Deploy Manual via Git

```bash
# No diretório visualization
git init
git add .
git commit -m "Deploy visualization"
git remote add origin https://github.com/seu-usuario/seu-repo.git
git push -u origin main
```

Depois conecte o repositório no Render.

## Notas

- Render oferece SSL gratuito
- O serviço pode "dormir" após inatividade (plano gratuito)
- Para evitar sleep, use plano pago ou configure health checks
