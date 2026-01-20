# Script PowerShell para iniciar o Crawler Java com variáveis de ambiente
# Uso: .\start-crawler.ps1

Write-Host "🚀 Iniciando Crawler Java..." -ForegroundColor Cyan

# Tentar carregar variáveis de ambiente de um arquivo .env se existir
$envFile = Join-Path $PSScriptRoot "..\..env"
if (Test-Path $envFile) {
    Write-Host "📄 Carregando variáveis de ambiente do arquivo .env..." -ForegroundColor Yellow
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]*?)\s*=\s*(.*?)\s*$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            if ($key -and $value) {
                [Environment]::SetEnvironmentVariable($key, $value, "Process")
                Write-Host "   $key = $value" -ForegroundColor Gray
            }
        }
    }
}

# Verificar se as variáveis de ambiente estão configuradas
if (-not $env:SUPABASE_URL -or -not $env:SUPABASE_KEY) {
    Write-Host "❌ Erro: Variáveis de ambiente não configuradas!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Configure as variáveis de ambiente:" -ForegroundColor Yellow
    Write-Host '  $env:SUPABASE_URL = "https://seu-projeto.supabase.co"' -ForegroundColor Gray
    Write-Host '  $env:SUPABASE_KEY = "sua-chave-supabase"' -ForegroundColor Gray
    Write-Host '  $env:SUPABASE_BUCKET = "tp3-data"  # Opcional, padrão é tp3-data' -ForegroundColor Gray
    Write-Host ""
    Write-Host "Ou crie um arquivo .env na raiz do projeto TP3 com:" -ForegroundColor Yellow
    Write-Host "  SUPABASE_URL=https://seu-projeto.supabase.co" -ForegroundColor Gray
    Write-Host "  SUPABASE_KEY=sua-chave-supabase" -ForegroundColor Gray
    Write-Host "  SUPABASE_BUCKET=tp3-data" -ForegroundColor Gray
    exit 1
}

# Verificar se o JAR existe
$jarPath = "target\crawler-1.0.0.jar"
if (-not (Test-Path $jarPath)) {
    Write-Host "📦 Compilando projeto..." -ForegroundColor Yellow
    mvn clean package
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Erro ao compilar!" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ Variáveis configuradas:" -ForegroundColor Green
Write-Host "   SUPABASE_URL: $env:SUPABASE_URL" -ForegroundColor Gray
Write-Host "   SUPABASE_BUCKET: $($env:SUPABASE_BUCKET ?? 'tp3-data')" -ForegroundColor Gray
Write-Host ""
Write-Host "▶️  Executando crawler..." -ForegroundColor Cyan
Write-Host ""

java -jar $jarPath
