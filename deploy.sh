#!/bin/bash

# Verificar que Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "Docker no está instalado. Por favor, instale Docker primero."
    exit 1
fi

# Verificar que docker-compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose no está instalado. Por favor, instale Docker Compose primero."
    exit 1
fi

# Crear directorio de logs si no existe
mkdir -p logs

# Detener contenedores existentes
echo "Deteniendo contenedores existentes..."
docker-compose down

# Construir imágenes
echo "Construyendo imágenes..."
docker-compose build

# Iniciar servicios
echo "Iniciando servicios..."
docker-compose up -d

# Esperar a que los servicios estén listos
echo "Esperando a que los servicios estén listos..."
sleep 30

# Ejecutar migraciones
echo "Ejecutando migraciones..."
docker-compose exec app ./scripts/run_migrations.sh

echo "¡Despliegue completado!"
echo "La aplicación está disponible en: http://localhost:5000"
echo "Grafana está disponible en: http://localhost:3000"
echo "Prometheus está disponible en: http://localhost:9090" 