#!/bin/bash

# Script para desplegar la aplicación Sistema POS Odata
# Uso: ./deploy.sh [staging|production]

set -e

ENVIRONMENT=$1
COMPOSE_FILE="docker-compose.production.yml"

if [ -z "$ENVIRONMENT" ]; then
    echo "Error: Debes especificar el ambiente (staging o production)."
    exit 1
fi

echo "🚀 Iniciando despliegue en $ENVIRONMENT..."

# Navegar al directorio del proyecto
cd /opt/pos-odata

# Verificar y cargar variables de entorno
if [ ! -f .env ]; then
    echo "❌ Error crítico: No se encontró el archivo .env en $(pwd). Abortando despliegue."
    exit 1
fi
echo "📄 Archivo .env encontrado."

# Determinar el nombre de la imagen (debe ser en minúsculas)
export APP_IMAGE_NAME="ghcr.io/$(echo $GITHUB_REPOSITORY | tr '[:upper:]' '[:lower:]')-backend"

# Determinar la etiqueta de la imagen Docker según el ambiente
IMAGE_TAG="latest" # Por defecto para producción (rama main)
if [ "$ENVIRONMENT" = "staging" ]; then
    IMAGE_TAG="develop" # Para staging (rama develop)
fi
export APP_IMAGE_TAG=$IMAGE_TAG
echo "ℹ️  Usando la imagen: ${APP_IMAGE_NAME}:${APP_IMAGE_TAG}"

# Crear backup antes del despliegue
echo "📦 Creando backup..."
if ! docker compose -f $COMPOSE_FILE run --rm backup; then
    echo "❌ Error crítico al crear el backup. Abortando despliegue."
    exit 1
fi

# Actualizar imágenes
echo "🔄 Actualizando imágenes Docker..."
docker compose -f $COMPOSE_FILE pull

# Desplegar nuevos contenedores
echo "🚀 Desplegando servicios..."
docker compose -f $COMPOSE_FILE up -d --remove-orphans

echo "⏳ Esperando que los servicios se estabilicen..."
sleep 30

echo "🔍 Verificando estado de los servicios..."
docker compose -f $COMPOSE_FILE ps

echo "✅ Despliegue en $ENVIRONMENT completado exitosamente."