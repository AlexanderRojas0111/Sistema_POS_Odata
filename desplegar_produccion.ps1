# Script de Despliegue de Producción - Sistema POS Sabrositas v2.0.0
# ====================================================================

param(
    [switch]$BuildOnly,
    [switch]$SkipFrontend,
    [switch]$SkipBackend,
    [string]$Environment = "production"
)

Write-Host "🚀 DESPLEGANDO SISTEMA POS SABROSITAS v2.0.0 EN PRODUCCIÓN" -ForegroundColor Green
Write-Host "=================================================================="
Write-Host "🍞 Las Arepas Cuadradas - Enterprise Edition" -ForegroundColor Yellow
Write-Host "=================================================================="

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

Write-Host ""
Show-Info "FASE 1: VALIDACIÓN PREVIA AL DESPLIEGUE"

# Verificar Docker
try {
    $dockerVersion = docker --version
    Show-Success "Docker: $dockerVersion"
} catch {
    Show-Error "Docker no encontrado. Instale Docker Desktop."
}

# Verificar Docker Compose
try {
    $dockerComposeVersion = docker-compose --version
    Show-Success "Docker Compose: $dockerComposeVersion"
} catch {
    Show-Error "Docker Compose no encontrado."
}

# Verificar archivos necesarios
$requiredFiles = @(
    "Dockerfile",
    "docker-compose.production.yml",
    "env.production.template",
    "requirements.txt",
    "main.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Show-Success "Archivo encontrado: $file"
    } else {
        Show-Error "Archivo requerido no encontrado: $file"
    }
}

Write-Host ""
Show-Info "FASE 2: PREPARACIÓN DE CONFIGURACIÓN"

# Crear archivo de entorno si no existe
if (-not (Test-Path ".env.production")) {
    Copy-Item "env.production.template" ".env.production"
    Show-Success "Archivo .env.production creado desde template"
} else {
    Show-Info "Archivo .env.production ya existe"
}

# Crear directorios necesarios
$directories = @("logs", "data", "backups", "ssl")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Show-Success "Directorio creado: $dir"
    }
}

Write-Host ""
Show-Info "FASE 3: CONSTRUCCIÓN DE CONTENEDORES"

if (-not $SkipBackend) {
    Show-Info "Construyendo imagen del backend..."
    try {
        docker build -t pos-sabrositas:latest -f Dockerfile .
        Show-Success "Imagen del backend construida exitosamente"
    } catch {
        Show-Error "Error construyendo imagen del backend"
    }
}

if (-not $SkipFrontend) {
    Show-Info "Construyendo frontend..."
    try {
        Set-Location frontend
        if (Test-Path "node_modules") {
            Show-Info "Usando node_modules existente"
        } else {
            Show-Info "Instalando dependencias del frontend..."
            npm install
        }
        
        Show-Info "Construyendo frontend para producción..."
        npm run build
        Show-Success "Frontend construido exitosamente"
        Set-Location ..
    } catch {
        Show-Error "Error construyendo frontend"
    }
}

if ($BuildOnly) {
    Show-Success "Construcción completada. Saliendo (BuildOnly especificado)."
    exit 0
}

Write-Host ""
Show-Info "FASE 4: DESPLIEGUE DE SERVICIOS"

# Detener servicios existentes
Show-Info "Deteniendo servicios existentes..."
try {
    docker-compose -f docker-compose.production.yml down --remove-orphans
    Show-Success "Servicios existentes detenidos"
} catch {
    Show-Info "No hay servicios previos para detener"
}

# Limpiar volúmenes si es necesario (opcional)
# docker-compose -f docker-compose.production.yml down -v

# Iniciar servicios
Show-Info "Iniciando servicios de producción..."
try {
    docker-compose -f docker-compose.production.yml up -d --build
    Show-Success "Servicios iniciados exitosamente"
} catch {
    Show-Error "Error iniciando servicios"
}

Write-Host ""
Show-Info "FASE 5: VERIFICACIÓN DE DESPLIEGUE"

# Esperar a que los servicios estén listos
Show-Info "Esperando a que los servicios estén listos..."
Start-Sleep -Seconds 30

# Verificar servicios
$services = @(
    @{Name="PostgreSQL"; Url="http://localhost:5432"; Container="pos-postgres-production"},
    @{Name="Redis"; Url="http://localhost:6379"; Container="pos-redis-production"},
    @{Name="Backend API"; Url="http://localhost:8000/api/v1/health"; Container="pos-app-production"},
    @{Name="Nginx"; Url="http://localhost:80"; Container="pos-nginx-production"}
)

foreach ($service in $services) {
    try {
        $containerStatus = docker inspect --format='{{.State.Status}}' $service.Container
        if ($containerStatus -eq "running") {
            Show-Success "$($service.Name): Contenedor ejecutándose"
        } else {
            Show-Error "$($service.Name): Contenedor no está ejecutándose ($containerStatus)"
        }
    } catch {
        Show-Error "$($service.Name): Error verificando contenedor"
    }
}

# Verificar health del backend
Show-Info "Verificando health check del backend..."
$maxAttempts = 10
$attempt = 1

while ($attempt -le $maxAttempts) {
    try {
        $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing -TimeoutSec 5
        if ($healthResponse.StatusCode -eq 200) {
            $healthData = $healthResponse.Content | ConvertFrom-Json
            Show-Success "Backend health check: $($healthData.status)"
            Show-Info "   Database: $($healthData.database)"
            Show-Info "   Timestamp: $($healthData.timestamp)"
            break
        }
    } catch {
        Show-Info "Intento $attempt de $maxAttempts`: Backend aun no responde, esperando..."
        Start-Sleep -Seconds 10
        $attempt++
    }
}

if ($attempt -gt $maxAttempts) {
    Show-Error "Backend no responde despues de $maxAttempts intentos"
}

Write-Host ""
Write-Host "🎉 DESPLIEGUE COMPLETADO EXITOSAMENTE" -ForegroundColor Green
Write-Host "=================================================================="

Write-Host ""
Show-Info "URLS DEL SISTEMA DESPLEGADO:"
Write-Host "   🌐 Frontend:        http://localhost:80" -ForegroundColor White
Write-Host "   🔧 Backend API:     http://localhost:8000" -ForegroundColor White
Write-Host "   💚 Health Check:    http://localhost:8000/api/v1/health" -ForegroundColor White
Write-Host "   📊 API Docs:        http://localhost:8000/docs" -ForegroundColor White

Write-Host ""
Show-Info "CREDENCIALES DEL SISTEMA:"
Write-Host "   🔑 SuperAdmin:      superadmin / SuperAdmin123!" -ForegroundColor White
Write-Host "   🔑 Global Admin:    globaladmin / Global123!" -ForegroundColor White
Write-Host "   🔑 Store Admin:     storeadmin1 / Store123!" -ForegroundColor White
Write-Host "   🔑 Tech Admin:      techadmin / TechAdmin123!" -ForegroundColor White

Write-Host ""
Show-Info "MONITOREO Y ADMINISTRACIÓN:"
Write-Host "   📊 Grafana:         http://localhost:3000 (admin/Sabrositas2024Grafana!)" -ForegroundColor White
Write-Host "   🔍 Prometheus:      http://localhost:9090" -ForegroundColor White
Write-Host "   📝 Logs:            docker-compose -f docker-compose.production.yml logs -f" -ForegroundColor White

Write-Host ""
Show-Info "COMANDOS ÚTILES:"
Write-Host "   Ver logs:           docker-compose -f docker-compose.production.yml logs -f" -ForegroundColor White
Write-Host "   Reiniciar:          docker-compose -f docker-compose.production.yml restart" -ForegroundColor White
Write-Host "   Detener:            docker-compose -f docker-compose.production.yml down" -ForegroundColor White
Write-Host "   Estado:             docker-compose -f docker-compose.production.yml ps" -ForegroundColor White

Write-Host ""
Write-Host "🍞 SISTEMA POS SABROSITAS DESPLEGADO Y LISTO!" -ForegroundColor Green
Write-Host "¡Listo para vender Las Arepas Cuadradas!" -ForegroundColor Yellow
Write-Host "=================================================================="
