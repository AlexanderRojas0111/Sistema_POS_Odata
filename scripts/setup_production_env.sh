#!/bin/bash
# Setup Production Environment - Sistema POS O'Data
# =================================================
# Script para configurar variables de entorno de producción de forma segura

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[OK] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARN] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Banner
echo -e "${BLUE}"
echo "=============================================================="
echo "        CONFIGURACION DE PRODUCCION - SISTEMA POS O'DATA     "
echo "=============================================================="
echo -e "${NC}"

# Verificar que estamos en el directorio correcto
if [ ! -f "minimal_pos.py" ]; then
    error "Ejecutar desde el directorio raiz del proyecto"
fi

# Crear archivo .env de producción
ENV_FILE=".env.production"
log "Creando archivo de variables de entorno: $ENV_FILE"

# Generar SECRET_KEY seguro
SECRET_KEY=$(openssl rand -hex 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_hex(32))")

# Configuración de base de datos
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"5432"}
DB_NAME=${DB_NAME:-"pos_production"}
DB_USER=${DB_USER:-"pos_user"}
DB_PASSWORD=${DB_PASSWORD:-$(openssl rand -base64 32 2>/dev/null || python3 -c "import secrets; print(secrets.token_urlsafe(32))")}

# Configuración de Redis
REDIS_HOST=${REDIS_HOST:-"localhost"}
REDIS_PORT=${REDIS_PORT:-"6379"}
REDIS_DB=${REDIS_DB:-"0"}

# Crear archivo .env
cat > "$ENV_FILE" << EOF
# Configuración de Producción - Sistema POS O'Data
# ================================================
# Generado automáticamente el $(date)

# Configuración básica
SECRET_KEY=$SECRET_KEY
FLASK_ENV=production
DEBUG=false
TESTING=false

# Base de datos
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME
SQLALCHEMY_DATABASE_URI=postgresql://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME

# Redis
REDIS_URL=redis://$REDIS_HOST:$REDIS_PORT/$REDIS_DB

# Configuración de CORS
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Configuración de email
MAIL_SERVER=smtp.yourdomain.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=noreply@yourdomain.com
MAIL_PASSWORD=your_email_password_here

# Configuración de backup
BACKUP_DIR=/backups
BACKUP_RETENTION_DAYS=30
BACKUP_MAX_FILES=50

# Configuración de monitoring
MONITORING_INTERVAL=60
MONITORING_ALERT_EMAIL=admin@yourdomain.com

# Configuración de archivos
UPLOAD_FOLDER=uploads
EOF

success "Archivo $ENV_FILE creado"

# Crear directorios necesarios
log "Creando directorios de producción..."
mkdir -p logs data backups uploads ssl nginx

# Establecer permisos seguros
chmod 700 backups
chmod 755 logs data uploads ssl nginx

success "Directorios creados con permisos seguros"

# Crear script de inicialización de base de datos
log "Creando script de inicialización de base de datos..."
cat > "scripts/init_production_db.sh" << 'EOF'
#!/bin/bash
# Inicialización de Base de Datos de Producción

set -e

# Cargar variables de entorno
if [ -f ".env.production" ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
fi

# Verificar conexión a PostgreSQL
if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; then
    echo "Error: No se puede conectar a PostgreSQL"
    exit 1
fi

# Crear base de datos si no existe
createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" 2>/dev/null || true

# Ejecutar migraciones (si las hay)
echo "Base de datos inicializada correctamente"
EOF

chmod +x scripts/init_production_db.sh
success "Script de inicialización de base de datos creado"

# Crear script de verificación de seguridad
log "Creando script de verificación de seguridad..."
cat > "scripts/security_check.sh" << 'EOF'
#!/bin/bash
# Verificación de Seguridad - Sistema POS O'Data

set -e

echo "🔒 VERIFICACION DE SEGURIDAD"
echo "============================="

# Verificar que no hay credenciales hardcodeadas
echo "Verificando credenciales hardcodeadas..."
if grep -r "password.*=" --include="*.py" --include="*.sh" . | grep -v "password.*=" | grep -v "os.environ"; then
    echo "❌ Posibles credenciales hardcodeadas encontradas"
    exit 1
fi

# Verificar permisos de archivos sensibles
echo "Verificando permisos de archivos..."
if [ -f ".env.production" ] && [ $(stat -c %a .env.production 2>/dev/null || stat -f %A .env.production 2>/dev/null) != "600" ]; then
    echo "❌ .env.production debe tener permisos 600"
    exit 1
fi

# Verificar que SECRET_KEY no es la por defecto
if grep -q "production-secret-key-change-this-immediately" .env.production 2>/dev/null; then
    echo "❌ SECRET_KEY no ha sido cambiada"
    exit 1
fi

echo "✅ Verificación de seguridad completada"
EOF

chmod +x scripts/security_check.sh
success "Script de verificación de seguridad creado"

# Mostrar resumen
echo -e "${GREEN}"
echo "=============================================================="
echo "              CONFIGURACION COMPLETADA"
echo "=============================================================="
echo -e "${NC}"

echo "📋 Archivos creados:"
echo "   • .env.production - Variables de entorno"
echo "   • scripts/init_production_db.sh - Inicialización de BD"
echo "   • scripts/security_check.sh - Verificación de seguridad"

echo ""
echo "🔧 Próximos pasos:"
echo "   1. Revisar y ajustar .env.production según tu entorno"
echo "   2. Configurar PostgreSQL y Redis"
echo "   3. Ejecutar: ./scripts/init_production_db.sh"
echo "   4. Ejecutar: ./scripts/security_check.sh"
echo "   5. Proceder con deployment: ./deploy_production.sh"

echo ""
echo "⚠️  IMPORTANTE:"
echo "   • Cambiar todas las credenciales por defecto"
echo "   • Configurar certificados SSL"
echo "   • Revisar configuración de firewall"
echo "   • Configurar backup automático"

success "Configuración de producción completada"
