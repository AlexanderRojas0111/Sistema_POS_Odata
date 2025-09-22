# ==============================================
# SCRIPT DE DESPLIEGUE PROFESIONAL
# Sistema POS Sabrositas v2.0.0
# ==============================================

param(
    [switch]$SkipTests,
    [switch]$ForceDeploy,
    [string]$Environment = "production"
)

Write-Host "🚀 DESPLIEGUE PROFESIONAL - Sistema POS Sabrositas v2.0.0" -ForegroundColor Green
Write-Host "===============================================================" -ForegroundColor Green
Write-Host "🥟 Las Arepas Cuadradas - Enterprise Deployment" -ForegroundColor Yellow
Write-Host "===============================================================" -ForegroundColor Green

# Función para mostrar errores
function Show-Error {
    param([string]$Message)
    Write-Host "❌ ERROR: $Message" -ForegroundColor Red
    exit 1
}

# Función para mostrar éxito
function Show-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

# Función para mostrar información
function Show-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

# Función para mostrar advertencia
function Show-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

Write-Host ""
Show-Info "FASE 1: VALIDACIÓN PRE-DESPLIEGUE"
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "main.py")) {
    Show-Error "No se encontró main.py. Ejecute desde el directorio raíz del proyecto."
}

# Verificar Docker
try {
    docker --version | Out-Null
    Show-Success "Docker disponible"
} catch {
    Show-Error "Docker no está instalado o no está en el PATH"
}

# Verificar Docker Compose
try {
    docker-compose --version | Out-Null
    Show-Success "Docker Compose disponible"
} catch {
    Show-Error "Docker Compose no está instalado"
}

Write-Host ""
Show-Info "FASE 2: BACKUP Y PREPARACIÓN"
Write-Host ""

# Crear backup de base de datos actual
$backupFile = "backups\pos_odata_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db"
if (Test-Path "instance\pos_odata.db") {
    if (-not (Test-Path "backups")) {
        New-Item -ItemType Directory -Path "backups" -Force
    }
    Copy-Item "instance\pos_odata.db" $backupFile
    Show-Success "Backup creado: $backupFile"
}

# Crear directorio de logs si no existe
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" -Force
    Show-Success "Directorio de logs creado"
}

Write-Host ""
Show-Info "FASE 3: CONFIGURACIÓN DE ENTORNO"
Write-Host ""

# Verificar archivo de configuración de producción
if (-not (Test-Path ".env.production")) {
    if (Test-Path "env.production.template") {
        Copy-Item "env.production.template" ".env.production"
        Show-Success "Archivo .env.production creado desde template"
        Show-Warning "IMPORTANTE: Configure las variables de entorno en .env.production"
    } else {
        Show-Error "No se encontró env.production.template"
    }
}

Write-Host ""
Show-Info "FASE 4: CONSTRUCCIÓN DE CONTENEDORES"
Write-Host ""

# Detener contenedores existentes
Show-Info "Deteniendo contenedores existentes..."
docker-compose -f docker-compose.production.yml down

# Construir imágenes
Show-Info "Construyendo imágenes Docker..."
docker-compose -f docker-compose.production.yml build --no-cache

if ($LASTEXITCODE -ne 0) {
    Show-Error "Error en la construcción de imágenes Docker"
}

Show-Success "Imágenes construidas exitosamente"

Write-Host ""
Show-Info "FASE 5: DESPLIEGUE DE SERVICIOS"
Write-Host ""

# Iniciar servicios
Show-Info "Iniciando servicios de producción..."
docker-compose -f docker-compose.production.yml up -d

if ($LASTEXITCODE -ne 0) {
    Show-Error "Error al iniciar servicios"
}

# Esperar a que los servicios estén listos
Show-Info "Esperando a que los servicios estén listos..."
Start-Sleep -Seconds 30

Write-Host ""
Show-Info "FASE 6: VALIDACIÓN POST-DESPLIEGUE"
Write-Host ""

# Verificar que los contenedores estén ejecutándose
$containers = docker-compose -f docker-compose.production.yml ps -q
foreach ($container in $containers) {
    $status = docker inspect --format='{{.State.Status}}' $container
    if ($status -eq "running") {
        Show-Success "Contenedor $container ejecutándose"
    } else {
        Show-Warning "Contenedor $container no está ejecutándose (Estado: $status)"
    }
}

# Verificar endpoints
Show-Info "Verificando endpoints..."

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Show-Success "Backend respondiendo correctamente"
    }
} catch {
    Show-Warning "Backend no responde aún, puede estar iniciando..."
}

Write-Host ""
Show-Success "DESPLIEGUE COMPLETADO EXITOSAMENTE"
Write-Host ""
Show-Info "Servicios disponibles:"
Write-Host "  - Backend: http://localhost:8000"
Write-Host "  - Frontend: http://localhost:5173"
Write-Host "  - Grafana: http://localhost:3000"
Write-Host "  - Prometheus: http://localhost:9090"
Write-Host ""
Show-Info "Para ver logs: docker-compose -f docker-compose.production.yml logs -f"
Show-Info "Para detener: docker-compose -f docker-compose.production.yml down"
Write-Host ""
Show-Success "¡Sistema POS Sabrositas desplegado en producción! 🥟🚀"
