#!/bin/bash

# Script de configuración para desarrollo del Sistema POS O'data
# Este script configura todo el entorno de desarrollo

set -e

echo "🚀 Configurando Sistema POS O'data para desarrollo..."

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si estamos en el directorio correcto
if [ ! -f "requirements.txt" ] || [ ! -f "docker-compose.yml" ]; then
    print_error "Debes ejecutar este script desde el directorio raíz del proyecto"
    exit 1
fi

print_status "Verificando requisitos del sistema..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 no está instalado. Por favor instálalo primero."
    exit 1
fi

# Verificar pip
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 no está instalado. Por favor instálalo primero."
    exit 1
fi

# Verificar Node.js
if ! command -v node &> /dev/null; then
    print_error "Node.js no está instalado. Por favor instálalo primero."
    exit 1
fi

# Verificar npm
if ! command -v npm &> /dev/null; then
    print_error "npm no está instalado. Por favor instálalo primero."
    exit 1
fi

# Verificar Docker
if ! command -v docker &> /dev/null; then
    print_warning "Docker no está instalado. Algunas funcionalidades no estarán disponibles."
fi

# Verificar Docker Compose
if ! command -v docker-compose &> /dev/null; then
    print_warning "Docker Compose no está instalado. Algunas funcionalidades no estarán disponibles."
fi

print_success "Requisitos del sistema verificados"

# Crear entorno virtual de Python
print_status "Configurando entorno virtual de Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Entorno virtual creado"
else
    print_status "Entorno virtual ya existe"
fi

# Activar entorno virtual
print_status "Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias de Python
print_status "Instalando dependencias de Python..."
pip install --upgrade pip
pip install -r requirements.txt
print_success "Dependencias de Python instaladas"

# Configurar variables de entorno
print_status "Configurando variables de entorno..."
if [ ! -f ".env" ]; then
    if [ -f "env.development" ]; then
        cp env.development .env
        print_success "Archivo .env creado desde env.development"
    else
        print_warning "No se encontró env.development, creando .env básico..."
        cat > .env << EOF
# Configuración de desarrollo
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/pos_odata_dev
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production
FLASK_ENV=development
FLASK_APP=app.main:app
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
LOG_LEVEL=DEBUG
REACT_APP_API_URL=http://localhost:5000/api
EOF
        print_success "Archivo .env básico creado"
    fi
else
    print_status "Archivo .env ya existe"
fi

# Instalar dependencias del frontend
print_status "Instalando dependencias del frontend..."
cd frontend
npm install --legacy-peer-deps
cd ..
print_success "Dependencias del frontend instaladas"

# Crear directorios necesarios
print_status "Creando directorios necesarios..."
mkdir -p logs
mkdir -p uploads
mkdir -p backups
print_success "Directorios creados"

# Inicializar base de datos
print_status "Inicializando base de datos..."
python scripts/init_db.py
print_success "Base de datos inicializada"

# Cargar datos de ejemplo
print_status "Cargando datos de ejemplo..."
python scripts/load_sample_data.py
print_success "Datos de ejemplo cargados"

# Configurar vector database para IA
print_status "Configurando base de datos vectorial para IA..."
python scripts/setup_vector_db.py
print_success "Base de datos vectorial configurada"

print_success "✅ Configuración completada exitosamente!"

echo ""
echo "🎉 El Sistema POS O'data está listo para desarrollo!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Iniciar servicios con Docker: docker-compose up -d"
echo "2. Iniciar backend: python app/main.py"
echo "3. Iniciar frontend: cd frontend && npm start"
echo ""
echo "🌐 URLs de acceso:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:5000"
echo "- Grafana: http://localhost:3000"
echo "- Prometheus: http://localhost:9090"
echo ""
echo "👤 Usuarios de prueba:"
echo "- Admin: admin@example.com / admin123"
echo "- Empleado: employee@example.com / employee123"
echo ""
echo "📚 Documentación:"
echo "- Manual de usuario: docs/user/MANUAL.md"
echo "- Documentación técnica: docs/technical/"
echo "" 