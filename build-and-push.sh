#!/bin/bash

# Script para fazer build e push das imagens Docker para o Docker Hub
# Uso: ./build-and-push.sh [version]
# Exemplo: ./build-and-push.sh v1.0.0

set -e

DOCKER_USER="duarteleal"
VERSION="${1:-latest}"

echo "=========================================="
echo "Building and pushing Docker images"
echo "Docker Hub User: $DOCKER_USER"
echo "Version: $VERSION"
echo "=========================================="

# Build das imagens
echo ""
echo "Building crawler image..."
docker build -t $DOCKER_USER/tp3-crawler:$VERSION ./crawler
docker tag $DOCKER_USER/tp3-crawler:$VERSION $DOCKER_USER/tp3-crawler:latest

echo ""
echo "Building processador image..."
docker build -t $DOCKER_USER/tp3-processador:$VERSION ./processador
docker tag $DOCKER_USER/tp3-processador:$VERSION $DOCKER_USER/tp3-processador:latest

echo ""
echo "Building xml-service image..."
docker build -t $DOCKER_USER/tp3-xml-service:$VERSION ./xml-service
docker tag $DOCKER_USER/tp3-xml-service:$VERSION $DOCKER_USER/tp3-xml-service:latest

echo ""
echo "Building bi-service image..."
docker build -t $DOCKER_USER/tp3-bi-service:$VERSION -f ./bi-service/Dockerfile .
docker tag $DOCKER_USER/tp3-bi-service:$VERSION $DOCKER_USER/tp3-bi-service:latest

echo ""
echo "Building visualization image..."
docker build -t $DOCKER_USER/tp3-visualization:$VERSION ./visualization
docker tag $DOCKER_USER/tp3-visualization:$VERSION $DOCKER_USER/tp3-visualization:latest

# Push das imagens
echo ""
echo "=========================================="
echo "Pushing images to Docker Hub..."
echo "=========================================="

echo ""
echo "Pushing crawler image..."
docker push $DOCKER_USER/tp3-crawler:$VERSION
docker push $DOCKER_USER/tp3-crawler:latest

echo ""
echo "Pushing processador image..."
docker push $DOCKER_USER/tp3-processador:$VERSION
docker push $DOCKER_USER/tp3-processador:latest

echo ""
echo "Pushing xml-service image..."
docker push $DOCKER_USER/tp3-xml-service:$VERSION
docker push $DOCKER_USER/tp3-xml-service:latest

echo ""
echo "Pushing bi-service image..."
docker push $DOCKER_USER/tp3-bi-service:$VERSION
docker push $DOCKER_USER/tp3-bi-service:latest

echo ""
echo "Pushing visualization image..."
docker push $DOCKER_USER/tp3-visualization:$VERSION
docker push $DOCKER_USER/tp3-visualization:latest

echo ""
echo "=========================================="
echo "All images pushed successfully!"
echo "=========================================="
echo ""
echo "Images available at:"
echo "  - $DOCKER_USER/tp3-crawler:$VERSION"
echo "  - $DOCKER_USER/tp3-processador:$VERSION"
echo "  - $DOCKER_USER/tp3-xml-service:$VERSION"
echo "  - $DOCKER_USER/tp3-bi-service:$VERSION"
echo "  - $DOCKER_USER/tp3-visualization:$VERSION"
echo ""
