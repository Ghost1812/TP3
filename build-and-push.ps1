# Script PowerShell para fazer build e push das imagens Docker para o Docker Hub
# Uso: .\build-and-push.ps1 [version]
# Exemplo: .\build-and-push.ps1 v1.0.0

param(
    [string]$Version = "latest"
)

$ErrorActionPreference = "Stop" 

$DOCKER_USER = "duarteleal"
$VERSION = $Version

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Building and pushing Docker images" -ForegroundColor Cyan
Write-Host "Docker Hub User: $DOCKER_USER" -ForegroundColor Cyan
Write-Host "Version: $VERSION" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Build das imagens
$buildErrors = @()

Write-Host ""
Write-Host "Building crawler image..." -ForegroundColor Yellow
try {
    docker build --progress=plain -t "${DOCKER_USER}/tp3-crawler:${VERSION}" ./crawler
    if ($LASTEXITCODE -ne 0) { throw "Build failed with exit code $LASTEXITCODE" }
    docker tag "${DOCKER_USER}/tp3-crawler:${VERSION}" "${DOCKER_USER}/tp3-crawler:latest"
    Write-Host "[OK] Crawler build successful" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Crawler build failed: $_" -ForegroundColor Red
    $buildErrors += "crawler"
}

Write-Host ""
Write-Host "Building processador image..." -ForegroundColor Yellow
try {
    docker build --progress=plain -t "${DOCKER_USER}/tp3-processador:${VERSION}" ./processador
    if ($LASTEXITCODE -ne 0) { throw "Build failed with exit code $LASTEXITCODE" }
    docker tag "${DOCKER_USER}/tp3-processador:${VERSION}" "${DOCKER_USER}/tp3-processador:latest"
    Write-Host "[OK] Processador build successful" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Processador build failed: $_" -ForegroundColor Red
    $buildErrors += "processador"
}

Write-Host ""
Write-Host "Building xml-service image..." -ForegroundColor Yellow
try {
    docker build --progress=plain -t "${DOCKER_USER}/tp3-xml-service:${VERSION}" ./xml-service
    if ($LASTEXITCODE -ne 0) { throw "Build failed with exit code $LASTEXITCODE" }
    docker tag "${DOCKER_USER}/tp3-xml-service:${VERSION}" "${DOCKER_USER}/tp3-xml-service:latest"
    Write-Host "[OK] XML Service build successful" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] XML Service build failed: $_" -ForegroundColor Red
    $buildErrors += "xml-service"
}

Write-Host ""
Write-Host "Building bi-service image..." -ForegroundColor Yellow
Write-Host "Note: This may take several minutes due to npm install..." -ForegroundColor Yellow
try {
    docker build --progress=plain -t "${DOCKER_USER}/tp3-bi-service:${VERSION}" -f ./bi-service/Dockerfile .
    if ($LASTEXITCODE -ne 0) { throw "Build failed with exit code $LASTEXITCODE" }
    docker tag "${DOCKER_USER}/tp3-bi-service:${VERSION}" "${DOCKER_USER}/tp3-bi-service:latest"
    Write-Host "[OK] BI Service build successful" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] BI Service build failed: $_" -ForegroundColor Red
    $buildErrors += "bi-service"
}

Write-Host ""
Write-Host "Building visualization image..." -ForegroundColor Yellow
try {
    docker build --progress=plain -t "${DOCKER_USER}/tp3-visualization:${VERSION}" ./visualization
    if ($LASTEXITCODE -ne 0) { throw "Build failed with exit code $LASTEXITCODE" }
    docker tag "${DOCKER_USER}/tp3-visualization:${VERSION}" "${DOCKER_USER}/tp3-visualization:latest"
    Write-Host "[OK] Visualization build successful" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Visualization build failed: $_" -ForegroundColor Red
    $buildErrors += "visualization"
}

if ($buildErrors.Count -gt 0) {
    Write-Host ""
    Write-Host "Warning: Some builds failed: $($buildErrors -join ', ')" -ForegroundColor Yellow
    Write-Host "Do you want to continue with pushing successful builds? (Y/N)" -ForegroundColor Yellow
    $response = Read-Host
    if ($response -ne "Y" -and $response -ne "y") {
        Write-Host "Aborted." -ForegroundColor Red
        exit 1
    }
}

# Push das imagens
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Pushing images to Docker Hub..." -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

$pushErrors = @()

if (-not $buildErrors.Contains("crawler")) {
    Write-Host ""
    Write-Host "Pushing crawler image..." -ForegroundColor Green
    try {
        docker push "${DOCKER_USER}/tp3-crawler:${VERSION}"
        if ($LASTEXITCODE -ne 0) { throw "Push failed with exit code $LASTEXITCODE" }
        docker push "${DOCKER_USER}/tp3-crawler:latest"
        if ($LASTEXITCODE -ne 0) { throw "Push failed with exit code $LASTEXITCODE" }
        Write-Host "[OK] Crawler pushed successfully" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Crawler push failed: $_" -ForegroundColor Red
        $pushErrors += "crawler"
    }
}

if (-not $buildErrors.Contains("processador")) {
    Write-Host ""
    Write-Host "Pushing processador image..." -ForegroundColor Green
    try {
        docker push "${DOCKER_USER}/tp3-processador:${VERSION}"
        if ($LASTEXITCODE -ne 0) { throw "Push failed with exit code $LASTEXITCODE" }
        docker push "${DOCKER_USER}/tp3-processador:latest"
        if ($LASTEXITCODE -ne 0) { throw "Push failed with exit code $LASTEXITCODE" }
        Write-Host "[OK] Processador pushed successfully" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Processador push failed: $_" -ForegroundColor Red
        $pushErrors += "processador"
    }
}

if (-not $buildErrors.Contains("xml-service")) {
    Write-Host ""
    Write-Host "Pushing xml-service image..." -ForegroundColor Green
    try {
        docker push "${DOCKER_USER}/tp3-xml-service:${VERSION}"
        if ($LASTEXITCODE -ne 0) { throw "Push failed with exit code $LASTEXITCODE" }
        docker push "${DOCKER_USER}/tp3-xml-service:latest"
        if ($LASTEXITCODE -ne 0) { throw "Push failed with exit code $LASTEXITCODE" }
        Write-Host "[OK] XML Service pushed successfully" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] XML Service push failed: $_" -ForegroundColor Red
        $pushErrors += "xml-service"
    }
}

if (-not $buildErrors.Contains("bi-service")) {
    Write-Host ""
    Write-Host "Pushing bi-service image..." -ForegroundColor Green
    try {
        docker push "${DOCKER_USER}/tp3-bi-service:${VERSION}"
        if ($LASTEXITCODE -ne 0) { throw "Push failed with exit code $LASTEXITCODE" }
        docker push "${DOCKER_USER}/tp3-bi-service:latest"
        if ($LASTEXITCODE -ne 0) { throw "Push failed with exit code $LASTEXITCODE" }
        Write-Host "[OK] BI Service pushed successfully" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] BI Service push failed: $_" -ForegroundColor Red
        $pushErrors += "bi-service"
    }
}

if (-not $buildErrors.Contains("visualization")) {
    Write-Host ""
    Write-Host "Pushing visualization image..." -ForegroundColor Green
    try {
        docker push "${DOCKER_USER}/tp3-visualization:${VERSION}"
        if ($LASTEXITCODE -ne 0) { throw "Push failed with exit code $LASTEXITCODE" }
        docker push "${DOCKER_USER}/tp3-visualization:latest"
        if ($LASTEXITCODE -ne 0) { throw "Push failed with exit code $LASTEXITCODE" }
        Write-Host "[OK] Visualization pushed successfully" -ForegroundColor Green
    } catch {
        Write-Host "[ERROR] Visualization push failed: $_" -ForegroundColor Red
        $pushErrors += "visualization"
    }
}

Write-Host ""
if ($pushErrors.Count -eq 0 -and $buildErrors.Count -eq 0) {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "All images pushed successfully!" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
} else {
    Write-Host "==========================================" -ForegroundColor Yellow
    Write-Host "Build/Push completed with some errors" -ForegroundColor Yellow
    Write-Host "==========================================" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Images available at:" -ForegroundColor White
if (-not $buildErrors.Contains("crawler")) {
    Write-Host "  [OK] ${DOCKER_USER}/tp3-crawler:${VERSION}"
}
if (-not $buildErrors.Contains("processador")) {
    Write-Host "  [OK] ${DOCKER_USER}/tp3-processador:${VERSION}"
}
if (-not $buildErrors.Contains("xml-service")) {
    Write-Host "  [OK] ${DOCKER_USER}/tp3-xml-service:${VERSION}"
}
if (-not $buildErrors.Contains("bi-service")) {
    Write-Host "  [OK] ${DOCKER_USER}/tp3-bi-service:${VERSION}"
}
if (-not $buildErrors.Contains("visualization")) {
    Write-Host "  [OK] ${DOCKER_USER}/tp3-visualization:${VERSION}"
}
Write-Host ""
