#!/bin/bash

# Script de despliegue para Staging
# Uso: ./scripts/deploy-staging.sh

set -e

echo "🚀 Iniciando despliegue a Staging..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.staging.yml" ]; then
    print_error "No se encontró docker-compose.staging.yml. Ejecuta desde el directorio raíz del proyecto."
    exit 1
fi

# Verificar que existe el archivo de variables de entorno
if [ ! -f "env.staging" ]; then
    print_error "No se encontró env.staging. Crea el archivo de variables de entorno."
    exit 1
fi

# Cargar variables de entorno
print_info "Cargando variables de entorno..."
export $(cat env.staging | grep -v '^#' | xargs)

# Verificar variables críticas
if [ -z "$SECRET_KEY" ] || [ -z "$JWT_SECRET_KEY" ]; then
    print_error "Variables SECRET_KEY y JWT_SECRET_KEY deben estar configuradas."
    exit 1
fi

# Crear directorios necesarios
print_info "Creando directorios necesarios..."
mkdir -p logs
mkdir -p uploads
mkdir -p backups
mkdir -p nginx/ssl

# Backup de la base de datos actual (si existe)
if docker ps | grep -q "pos-odata-staging-db"; then
    print_info "Creando backup de la base de datos..."
    docker exec pos-odata-staging-db pg_dump -U postgres pos_odata_staging > backups/staging_backup_$(date +%Y%m%d_%H%M%S).sql
    print_status "Backup creado exitosamente"
fi

# Detener servicios existentes
print_info "Deteniendo servicios existentes..."
docker-compose -f docker-compose.staging.yml down --remove-orphans

# Limpiar imágenes antiguas (opcional)
if [ "$1" = "--clean" ]; then
    print_info "Limpiando imágenes Docker..."
    docker system prune -f
fi

# Construir y levantar servicios
print_info "Construyendo y levantando servicios..."
docker-compose -f docker-compose.staging.yml up -d --build

# Esperar a que los servicios estén listos
print_info "Esperando a que los servicios estén listos..."
sleep 30

# Verificar health checks
print_info "Verificando health checks..."

# Verificar base de datos
if docker exec pos-odata-staging-db pg_isready -U postgres; then
    print_status "Base de datos PostgreSQL lista"
else
    print_error "Base de datos PostgreSQL no está lista"
    exit 1
fi

# Verificar Redis
if docker exec pos-odata-staging-redis redis-cli ping | grep -q "PONG"; then
    print_status "Redis lista"
else
    print_error "Redis no está listo"
    exit 1
fi

# Verificar aplicación
if curl -f http://localhost:5000/health > /dev/null 2>&1; then
    print_status "Aplicación backend lista"
else
    print_error "Aplicación backend no está lista"
    exit 1
fi

# Verificar frontend
if curl -f http://localhost:3001 > /dev/null 2>&1; then
    print_status "Frontend lista"
else
    print_error "Frontend no está listo"
    exit 1
fi

# Ejecutar migraciones de base de datos
print_info "Ejecutando migraciones de base de datos..."
docker exec pos-odata-staging-app flask db upgrade

# Ejecutar tests de integración
print_info "Ejecutando tests de integración..."
docker exec pos-odata-staging-app python -m pytest tests/ -v --tb=short

# Verificar monitoreo
print_info "Verificando servicios de monitoreo..."

if curl -f http://localhost:9091 > /dev/null 2>&1; then
    print_status "Prometheus lista"
else
    print_warning "Prometheus no está accesible"
fi

if curl -f http://localhost:3002 > /dev/null 2>&1; then
    print_status "Grafana lista"
else
    print_warning "Grafana no está accesible"
fi

# Mostrar información del despliegue
echo ""
print_status "🎉 Despliegue a Staging completado exitosamente!"
echo ""
echo "📊 Servicios disponibles:"
echo "   • Backend API: http://localhost:5000"
echo "   • Frontend: http://localhost:3001"
echo "   • Nginx: http://localhost:8080"
echo "   • Prometheus: http://localhost:9091"
echo "   • Grafana: http://localhost:3002 (admin/admin)"
echo ""
echo "🔍 Health Check: http://localhost:5000/health"
echo "📝 Logs: docker-compose -f docker-compose.staging.yml logs -f"
echo "🛑 Detener: docker-compose -f docker-compose.staging.yml down"
echo ""

# Mostrar logs recientes
print_info "Últimos logs de la aplicación:"
docker-compose -f docker-compose.staging.yml logs --tail=20 app 