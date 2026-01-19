# Script para fazer build rápido (sem push) - útil para testar
# Uso: .\build-fast.ps1 [version]

param(
    [string]$Version = "latest"
)

$ErrorActionPreference = "Continue"  # Continuar mesmo se uma falhar

$DOCKER_USER = "duarteleal"
$VERSION = $Version

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Fast build (no push) - Testing images" -ForegroundColor Cyan
Write-Host "Version: $VERSION" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$services = @("crawler", "processador", "xml-service", "bi-service", "visualization")
$success = @()
$failed = @()

foreach ($service in $services) {
    Write-Host ""
    Write-Host "Building $service..." -ForegroundColor Yellow
    
    $dockerfile = "./${service}/Dockerfile"
    $context = "./${service}"
    
    if ($service -eq "bi-service") {
        $dockerfile = "./bi-service/Dockerfile"
        $context = "."
        Write-Host "  (This may take 5-10 minutes)" -ForegroundColor Yellow
    }
    
    docker build -t "${DOCKER_USER}/tp3-${service}:${VERSION}" -f $dockerfile $context 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        docker tag "${DOCKER_USER}/tp3-${service}:${VERSION}" "${DOCKER_USER}/tp3-${service}:latest" 2>&1 | Out-Null
        Write-Host "[OK] $service" -ForegroundColor Green
        $success += $service
    } else {
        Write-Host "[FAILED] $service" -ForegroundColor Red
        $failed += $service
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Build Summary" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Successful: $($success.Count)" -ForegroundColor Green
Write-Host "Failed: $($failed.Count)" -ForegroundColor $(if ($failed.Count -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($success.Count -gt 0) {
    Write-Host "Successfully built:" -ForegroundColor Green
    $success | ForEach-Object { Write-Host "  - $_" }
}

if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "Failed:" -ForegroundColor Red
    $failed | ForEach-Object { Write-Host "  - $_" }
}

Write-Host ""
