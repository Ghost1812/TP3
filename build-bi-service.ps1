# Script para fazer build apenas do bi-service (útil para debug)
# Uso: .\build-bi-service.ps1 [version]

param(
    [string]$Version = "latest"
)

$ErrorActionPreference = "Stop"

$DOCKER_USER = "duarteleal"
$VERSION = $Version

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Building BI Service image only" -ForegroundColor Cyan
Write-Host "Docker Hub User: $DOCKER_USER" -ForegroundColor Cyan
Write-Host "Version: $VERSION" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Building bi-service image..." -ForegroundColor Yellow
Write-Host "Note: npm install may take several minutes..." -ForegroundColor Yellow
Write-Host ""

try {
    # Build com output detalhado
    docker build --progress=plain --no-cache -t "${DOCKER_USER}/tp3-bi-service:${VERSION}" -f ./bi-service/Dockerfile .
    
    Write-Host ""
    Write-Host "Tagging as latest..." -ForegroundColor Yellow
    docker tag "${DOCKER_USER}/tp3-bi-service:${VERSION}" "${DOCKER_USER}/tp3-bi-service:latest"
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "BI Service build successful!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Image: ${DOCKER_USER}/tp3-bi-service:${VERSION}" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "Build failed!" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Tips:" -ForegroundColor Yellow
    Write-Host "  - Check your internet connection" -ForegroundColor Yellow
    Write-Host "  - Try: docker system prune -a (to clear cache)" -ForegroundColor Yellow
    Write-Host "  - Check npm registry: npm config get registry" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}
