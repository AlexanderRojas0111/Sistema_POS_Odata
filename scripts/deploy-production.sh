#!/bin/bash

# Script de despliegue para Producción
# Uso: ./scripts/deploy-production.sh [--force]

set -e

echo "🚀 Iniciando despliegue a Producción..."

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
if [ ! -f "docker-compose.production.yml" ]; then
    print_error "No se encontró docker-compose.production.yml. Ejecuta desde el directorio raíz del proyecto."
    exit 1
fi

# Verificar que existe el archivo de variables de entorno
if [ ! -f "env.production" ]; then
    print_error "No se encontró env.production. Crea el archivo de variables de entorno."
    exit 1
fi

# Verificar que no estamos en desarrollo
if [ "$FLASK_ENV" = "development" ]; then
    print_error "No se puede desplegar a producción desde entorno de desarrollo."
    exit 1
fi

# Confirmación de seguridad (a menos que se use --force)
if [ "$1" != "--force" ]; then
    echo ""
    print_warning "⚠️  ADVERTENCIA: Estás a punto de desplegar a PRODUCCIÓN"
    echo ""
    echo "Esto afectará a usuarios reales. ¿Estás seguro?"
    echo ""
    read -p "Escribe 'PRODUCCION' para confirmar: " confirmation
    
    if [ "$confirmation" != "PRODUCCION" ]; then
        print_error "Despliegue cancelado."
        exit 1
    fi
fi

# Cargar variables de entorno
print_info "Cargando variables de entorno..."
export $(cat env.production | grep -v '^#' | xargs)

# Verificar variables críticas de producción
print_info "Verificando variables críticas..."

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "CHANGE_THIS_SECRET_KEY_IN_PRODUCTION_USE_STRONG_RANDOM_KEY" ]; then
    print_error "SECRET_KEY debe estar configurada con una clave fuerte en producción."
    exit 1
fi

if [ -z "$JWT_SECRET_KEY" ] || [ "$JWT_SECRET_KEY" = "CHANGE_THIS_JWT_SECRET_KEY_IN_PRODUCTION_USE_STRONG_RANDOM_KEY" ]; then
    print_error "JWT_SECRET_KEY debe estar configurada con una clave fuerte en producción."
    exit 1
fi

if [ -z "$POSTGRES_PASSWORD" ] || [ "$POSTGRES_PASSWORD" = "CHANGE_THIS_PASSWORD_IN_PRODUCTION" ]; then
    print_error "POSTGRES_PASSWORD debe estar configurada en producción."
    exit 1
fi

if [ -z "$REDIS_PASSWORD" ] || [ "$REDIS_PASSWORD" = "CHANGE_THIS_REDIS_PASSWORD_IN_PRODUCTION" ]; then
    print_error "REDIS_PASSWORD debe estar configurada en producción."
    exit 1
fi

print_status "Variables críticas verificadas"

# Crear directorios necesarios
print_info "Creando directorios necesarios..."
mkdir -p logs
mkdir -p uploads
mkdir -p backups
mkdir -p nginx/ssl
mkdir -p certbot/conf
mkdir -p certbot/www

# Backup completo de la base de datos actual
if docker ps | grep -q "pos-odata-prod-db"; then
    print_info "Creando backup completo de la base de datos..."
    timestamp=$(date +%Y%m%d_%H%M%S)
    backup_file="backups/production_backup_${timestamp}.sql"
    docker exec pos-odata-prod-db pg_dump -U $POSTGRES_USER $POSTGRES_DB > "$backup_file"
    
    # Comprimir backup
    gzip "$backup_file"
    print_status "Backup creado: ${backup_file}.gz"
fi

# Verificar espacio en disco
print_info "Verificando espacio en disco..."
available_space=$(df / | awk 'NR==2 {print $4}')
if [ "$available_space" -lt 10485760 ]; then  # 10GB en KB
    print_warning "Poco espacio en disco disponible. Considera limpiar antes del despliegue."
fi

# Detener servicios existentes
print_info "Deteniendo servicios existentes..."
docker-compose -f docker-compose.production.yml down --remove-orphans

# Limpiar recursos Docker (opcional)
if [ "$1" = "--clean" ]; then
    print_info "Limpiando recursos Docker..."
    docker system prune -f
fi

# Construir y levantar servicios
print_info "Construyendo y levantando servicios..."
docker-compose -f docker-compose.production.yml up -d --build

# Esperar a que los servicios estén listos
print_info "Esperando a que los servicios estén listos..."
sleep 60

# Verificar health checks
print_info "Verificando health checks..."

# Verificar base de datos
if docker exec pos-odata-prod-db pg_isready -U $POSTGRES_USER; then
    print_status "Base de datos PostgreSQL lista"
else
    print_error "Base de datos PostgreSQL no está lista"
    exit 1
fi

# Verificar Redis
if docker exec pos-odata-prod-redis redis-cli -a $REDIS_PASSWORD ping | grep -q "PONG"; then
    print_status "Redis lista"
else
    print_error "Redis no está listo"
    exit 1
fi

# Verificar aplicación (múltiples instancias)
app_healthy=0
for i in {1..10}; do
    if curl -f http://localhost:5000/health > /dev/null 2>&1; then
        app_healthy=1
        break
    fi
    sleep 5
done

if [ $app_healthy -eq 1 ]; then
    print_status "Aplicación backend lista"
else
    print_error "Aplicación backend no está lista"
    exit 1
fi

# Verificar frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    print_status "Frontend lista"
else
    print_error "Frontend no está listo"
    exit 1
fi

# Ejecutar migraciones de base de datos
print_info "Ejecutando migraciones de base de datos..."
docker exec pos-odata-prod-app flask db upgrade

# Ejecutar tests de integración críticos
print_info "Ejecutando tests de integración críticos..."
docker exec pos-odata-prod-app python -m pytest tests/test_api.py::test_health_check -v

# Verificar SSL (si está configurado)
if [ -n "$DOMAIN_NAME" ]; then
    print_info "Verificando certificado SSL..."
    if curl -f https://$DOMAIN_NAME/health > /dev/null 2>&1; then
        print_status "SSL configurado correctamente"
    else
        print_warning "SSL no está configurado o no es accesible"
    fi
fi

# Verificar monitoreo
print_info "Verificando servicios de monitoreo..."

if curl -f http://localhost:9090 > /dev/null 2>&1; then
    print_status "Prometheus lista"
else
    print_warning "Prometheus no está accesible"
fi

if curl -f http://localhost:3001 > /dev/null 2>&1; then
    print_status "Grafana lista"
else
    print_warning "Grafana no está accesible"
fi

if curl -f http://localhost:9093 > /dev/null 2>&1; then
    print_status "Alertmanager lista"
else
    print_warning "Alertmanager no está accesible"
fi

# Verificar logs de errores
print_info "Verificando logs de errores..."
error_count=$(docker-compose -f docker-compose.production.yml logs app | grep -i "error\|exception" | wc -l)
if [ "$error_count" -gt 0 ]; then
    print_warning "Se encontraron $error_count errores en los logs"
    docker-compose -f docker-compose.production.yml logs app | grep -i "error\|exception" | tail -5
else
    print_status "No se encontraron errores críticos en los logs"
fi

# Mostrar información del despliegue
echo ""
print_status "🎉 Despliegue a Producción completado exitosamente!"
echo ""
echo "📊 Servicios disponibles:"
echo "   • Backend API: http://localhost:5000"
echo "   • Frontend: http://localhost:3000"
echo "   • Nginx: http://localhost:80, https://localhost:443"
echo "   • Prometheus: http://localhost:9090"
echo "   • Grafana: http://localhost:3001"
echo "   • Alertmanager: http://localhost:9093"
echo ""
echo "🔍 Health Check: http://localhost:5000/health"
echo "📝 Logs: docker-compose -f docker-compose.production.yml logs -f"
echo "🛑 Detener: docker-compose -f docker-compose.production.yml down"
echo ""

# Mostrar métricas de rendimiento
print_info "Métricas de rendimiento:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"

# Mostrar logs recientes
print_info "Últimos logs de la aplicación:"
docker-compose -f docker-compose.production.yml logs --tail=10 app 