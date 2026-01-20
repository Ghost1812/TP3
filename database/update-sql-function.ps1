# Script PowerShell para atualizar a função SQL no Supabase
# Uso: .\update-sql-function.ps1

Write-Host "🔄 Atualizando função SQL contar_ativos_por_tipo..." -ForegroundColor Cyan

# Verificar se SUPABASE_DB_URL está configurado
if (-not $env:SUPABASE_DB_URL) {
    Write-Host "❌ Erro: SUPABASE_DB_URL não está configurado!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Configure a variável de ambiente:" -ForegroundColor Yellow
    Write-Host '  $env:SUPABASE_DB_URL = "postgresql://..."' -ForegroundColor Gray
    Write-Host ""
    Write-Host "Ou execute o SQL manualmente no Supabase SQL Editor:" -ForegroundColor Yellow
    Write-Host "  Arquivo: database\update-contar-ativos-por-tipo.sql" -ForegroundColor Gray
    exit 1
}

# Executar script Python
$pythonScript = Join-Path $PSScriptRoot "update_function.py"
python $pythonScript

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Função SQL atualizada com sucesso!" -ForegroundColor Green
    Write-Host "Agora a contagem mostra países únicos em vez de registros totais." -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "❌ Erro ao atualizar função SQL." -ForegroundColor Red
    Write-Host "Execute manualmente o SQL no Supabase Dashboard > SQL Editor" -ForegroundColor Yellow
}
