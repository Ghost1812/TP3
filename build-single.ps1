# Script para fazer build de uma única imagem (útil para debug e acompanhar progresso)
# Uso: .\build-single.ps1 [service] [version]
# Exemplo: .\build-single.ps1 crawler v1.0.0

param(
    [Parameter(Mandatory=$true)]
    [string]$Service,
    
    [string]$Version = "latest"
)

$ErrorActionPreference = "Stop"

$DOCKER_USER = "duarteleal"
$VERSION = $Version

$services = @{
    "crawler" = @{
        "path" = "./crawler"
        "dockerfile" = "./crawler/Dockerfile"
    }
    "processador" = @{
        "path" = "./processador"
        "dockerfile" = "./processador/Dockerfile"
    }
    "xml-service" = @{
        "path" = "./xml-service"
        "dockerfile" = "./xml-service/Dockerfile"
    }
    "bi-service" = @{
        "path" = "."
        "dockerfile" = "./bi-service/Dockerfile"
    }
    "visualization" = @{
        "path" = "./visualization"
        "dockerfile" = "./visualization/Dockerfile"
    }
}

if (-not $services.ContainsKey($Service)) {
    Write-Host "Error: Service '$Service' not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Available services:" -ForegroundColor Yellow
    $services.Keys | ForEach-Object { Write-Host "  - $_" }
    exit 1
}

$serviceConfig = $services[$Service]
$imageName = "${DOCKER_USER}/tp3-${Service}:${VERSION}"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Building single image: $Service" -ForegroundColor Cyan
Write-Host "Image: $imageName" -ForegroundColor Cyan
Write-Host "Version: $VERSION" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

if ($Service -eq "bi-service") {
    Write-Host "Note: bi-service build may take 5-10 minutes due to npm install" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Starting build..." -ForegroundColor Yellow
Write-Host ""

try {
    docker build --progress=plain -t $imageName -f $serviceConfig.dockerfile $serviceConfig.path
    
    if ($LASTEXITCODE -ne 0) {
        throw "Build failed with exit code $LASTEXITCODE"
    }
    
    Write-Host ""
    Write-Host "Tagging as latest..." -ForegroundColor Yellow
    docker tag $imageName "${DOCKER_USER}/tp3-${Service}:latest"
    
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "[OK] Build successful!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Image created: $imageName" -ForegroundColor White
    Write-Host "Image tagged: ${DOCKER_USER}/tp3-${Service}:latest" -ForegroundColor White
    Write-Host ""
    Write-Host "To push this image, run:" -ForegroundColor Yellow
    Write-Host "  docker push $imageName" -ForegroundColor White
    Write-Host "  docker push ${DOCKER_USER}/tp3-${Service}:latest" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "[ERROR] Build failed!" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Red
    Write-Host ""
    exit 1
}
