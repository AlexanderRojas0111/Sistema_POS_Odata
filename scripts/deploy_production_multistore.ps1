# Script de Despliegue Multi-Tienda para Producción
# ==================================================
# Sistema POS Sabrositas v2.0.0 - Enterprise Multi-Store Deployment

param(
    [switch]$InitDatabase,
    [switch]$SkipFrontend,
    [switch]$SkipBackend,
    [switch]$SkipMonitoring,
    [switch]$SkipTests,
    [string]$Environment = "production"
)

Write-Host "DESPLEGANDO SISTEMA MULTI-TIENDA POS SABROSITAS v2.0.0" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "Enterprise Multi-Store Production Environment" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Green

# Función para mostrar errores
function Show-Error {
    param([string]$Message)
    Write-Host "ERROR: $Message" -ForegroundColor Red
    exit 1
}

# Función para mostrar éxito
function Show-Success {
    param([string]$Message)
    Write-Host "OK: $Message" -ForegroundColor Green
}

# Función para mostrar información
function Show-Info {
    param([string]$Message)
    Write-Host "INFO: $Message" -ForegroundColor Cyan
}

# Función para mostrar advertencia
function Show-Warning {
    param([string]$Message)
    Write-Host "WARN: $Message" -ForegroundColor Yellow
}

Write-Host ""
Show-Info "FASE 1: VALIDACIÓN DE ENTORNO DE PRODUCCIÓN"
Write-Host ""

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

# Verificar archivos necesarios para producción
$requiredFiles = @(
    "docker-compose.production.yml",
    "env.production.template",
    "requirements.txt",
    "main.py",
    "scripts/init-db.sql",
    "scripts/init_production_multistore.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Show-Success "Archivo encontrado: $file"
    } else {
        Show-Error "Archivo requerido no encontrado: $file"
    }
}

Write-Host ""
Show-Info "FASE 2: PREPARACIÓN DE CONFIGURACIÓN DE PRODUCCIÓN"
Write-Host ""

# Crear archivo de entorno de producción
if (-not (Test-Path ".env.production")) {
    Copy-Item "env.production.template" ".env.production"
    Show-Success "Archivo .env.production creado desde template"
    Show-Warning "IMPORTANTE: Configure las variables de entorno en .env.production antes de continuar"
    Show-Info "Editando variables críticas..."
    
    # Generar claves seguras
    $secretKey = [System.Web.Security.Membership]::GeneratePassword(32, 8)
    $jwtKey = [System.Web.Security.Membership]::GeneratePassword(32, 8)
    $redisPassword = [System.Web.Security.Membership]::GeneratePassword(16, 4)
    $postgresPassword = [System.Web.Security.Membership]::GeneratePassword(20, 6)
    
    # Actualizar archivo .env.production con valores seguros
    (Get-Content ".env.production") |
    ForEach-Object {
        $_ -replace "pos-sabrositas-2024-production-key-ultra-secure-32chars", $secretKey `
           -replace "jwt-sabrositas-2024-ultra-secure-production-key-32chars", $jwtKey `
           -replace "Sabrositas2024Redis!", $redisPassword `
           -replace "Sabrositas2024SecureDB!", $postgresPassword
    } | Set-Content ".env.production"
    
    Show-Success "Variables de seguridad generadas automáticamente"
} else {
    Show-Info "Archivo .env.production ya existe"
    $placeholders = @(
        "pos-sabrositas-2024-production-key-ultra-secure-32chars",
        "jwt-sabrositas-2024-ultra-secure-production-key-32chars",
        "Sabrositas2024Redis!",
        "Sabrositas2024SecureDB!"
    )
    foreach ($p in $placeholders) {
        if (Select-String -Path ".env.production" -Pattern [regex]::Escape($p) -SimpleMatch) {
            Show-Error "El archivo .env.production aún contiene valores de ejemplo ($p). Actualícelo antes de desplegar."
        }
    }
}

# Crear directorios necesarios para producción
$directories = @(
    "logs", "data", "backups", "ssl", 
    "monitoring/logs", "monitoring/data",
    "postgres_data", "redis_data"
)

foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Show-Success "Directorio creado: $dir"
    }
}

Write-Host ""
Show-Info "FASE 3: CONSTRUCCIÓN DE IMÁGENES ENTERPRISE"
Write-Host ""

# Ejecutar tests rápidos antes de construir (opcional)
if (-not $SkipTests -and (Test-Path "tests")) {
    Show-Info "Ejecutando tests rápidos (pytest -q)..."
    try {
        python -m pytest tests -q
        if ($LASTEXITCODE -ne 0) {
            Show-Error "Tests fallaron, usa -SkipTests para omitir o corrige antes de desplegar."
        }
    } catch {
        Show-Warning "No se pudieron ejecutar tests: $($_.Exception.Message)"
    }
}

if (-not $SkipBackend) {
    Show-Info "Construyendo imagen del backend para producción..."
    try {
        docker build -t pos-sabrositas:production -f Dockerfile .
        Show-Success "Imagen del backend construida exitosamente"
    } catch {
        Show-Error "Error construyendo imagen del backend"
    }
}

if (-not $SkipFrontend) {
    Show-Info "Construyendo frontend para producción..."
    try {
        Set-Location frontend
        
        if (-not (Test-Path "node_modules")) {
            Show-Info "Instalando dependencias del frontend..."
            npm install --production
        }
        
        Show-Info "Construyendo frontend optimizado para producción..."
        $env:NODE_ENV = "production"
        npm run build:production
        Show-Success "Frontend construido exitosamente"
        
        Set-Location ..
    } catch {
        Show-Error "Error construyendo frontend"
    }
}

Write-Host ""
Show-Info "FASE 4: DESPLIEGUE DE INFRAESTRUCTURA DE PRODUCCIÓN"
Write-Host ""

# Detener servicios existentes
Show-Info "Deteniendo servicios existentes..."
try {
    docker-compose -f docker-compose.production.yml down --remove-orphans
    Show-Success "Servicios existentes detenidos"
} catch {
    Show-Info "No hay servicios previos para detener"
}

# Limpiar volúmenes si se solicita reinicialización de BD
if ($InitDatabase) {
    Show-Warning "Eliminando datos de base de datos existentes..."
    docker-compose -f docker-compose.production.yml down -v
    Show-Info "Volúmenes eliminados - se realizará inicialización completa"
}

# Iniciar servicios de producción
Show-Info "Iniciando servicios de producción multi-tienda..."
try {
    docker-compose -f docker-compose.production.yml up -d --build
    Show-Success "Servicios iniciados exitosamente"
} catch {
    Show-Error "Error iniciando servicios"
}

Write-Host ""
Show-Info "FASE 5: INICIALIZACIÓN DE BASE DE DATOS MULTI-TIENDA"
Write-Host ""

# Esperar a que PostgreSQL esté listo
Show-Info "Esperando a que PostgreSQL esté listo..."
$maxAttempts = 30
$attempt = 1

while ($attempt -le $maxAttempts) {
    try {
        $pgStatus = docker exec pos-postgres-production pg_isready -U pos_user -d pos_odata
        if ($pgStatus -match "accepting connections") {
            Show-Success "PostgreSQL está listo"
            break
        }
    } catch {
        Show-Info "Intento $attempt de $maxAttempts`: PostgreSQL aún no está listo..."
        Start-Sleep -Seconds 5
        $attempt++
    }
}

if ($attempt -gt $maxAttempts) {
    Show-Error "PostgreSQL no respondió después de $maxAttempts intentos"
}

# Ejecutar inicialización de base de datos multi-tienda
Show-Info "Ejecutando inicialización de base de datos multi-tienda..."
try {
    docker exec pos-app-production python scripts/init_production_multistore.py
    Show-Success "Base de datos multi-tienda inicializada correctamente"
} catch {
    Show-Warning "Error en inicialización automática. Ejecutando manualmente..."
    try {
        docker exec -it pos-app-production python scripts/init_production_multistore.py
        Show-Success "Inicialización manual completada"
    } catch {
        Show-Error "Error en inicialización de base de datos"
    }
}

Write-Host ""
Show-Info "FASE 6: CONFIGURACIÓN DE MONITOREO ENTERPRISE"
Write-Host ""

if (-not $SkipMonitoring) {
    Show-Info "Configurando stack de monitoreo..."
    
    # Iniciar servicios de monitoreo
    try {
        Set-Location monitoring
        docker-compose up -d
        Show-Success "Stack de monitoreo iniciado"
        Set-Location ..
    } catch {
        Show-Warning "Error iniciando monitoreo - continuando sin monitoreo"
    }
}

Write-Host ""
Show-Info "FASE 7: VERIFICACIÓN DE DESPLIEGUE MULTI-TIENDA"
Write-Host ""

# Esperar a que todos los servicios estén listos
Show-Info "Esperando a que todos los servicios estén listos..."
Start-Sleep -Seconds 45

# Verificar servicios críticos
$services = @(
    @{Name="PostgreSQL"; Container="pos-postgres-production"},
    @{Name="Redis"; Container="pos-redis-production"},
    @{Name="Backend API"; Container="pos-app-production"},
    @{Name="Nginx"; Container="pos-nginx-production"}
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
Show-Info "Verificando health check del sistema multi-tienda..."
$maxAttempts = 15
$attempt = 1

while ($attempt -le $maxAttempts) {
    try {
        $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing -TimeoutSec 10
        if ($healthResponse.StatusCode -eq 200) {
            $healthData = $healthResponse.Content | ConvertFrom-Json
            Show-Success "Sistema health check: $($healthData.status)"
            Show-Info "   Database: $($healthData.database)"
            Show-Info "   Multi-Store: $($healthData.stores_count) tiendas configuradas"
            Show-Info "   Timestamp: $($healthData.timestamp)"
            break
        }
    } catch {
        Show-Info "Intento $attempt de $maxAttempts`: Sistema aún no responde, esperando..."
        Start-Sleep -Seconds 10
        $attempt++
    }
}

if ($attempt -gt $maxAttempts) {
    Show-Error "Sistema no responde después de $maxAttempts intentos"
}

# Verificar tiendas configuradas
Show-Info "Verificando configuración multi-tienda..."
try {
    $storesResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/stores" -UseBasicParsing -TimeoutSec 10
    if ($storesResponse.StatusCode -eq 200) {
        $storesData = $storesResponse.Content | ConvertFrom-Json
        Show-Success "Tiendas configuradas: $($storesData.count)"
        
        foreach ($store in $storesData.stores) {
            Show-Info "   • $($store.code) - $($store.name) ($($store.store_type))"
        }
    }
} catch {
    Show-Warning "No se pudo verificar configuración de tiendas (puede requerir autenticación)"
}

Write-Host ""
Write-Host "DESPLIEGUE MULTI-TIENDA COMPLETADO EXITOSAMENTE" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green

Write-Host ""
Show-Info "URLS DEL SISTEMA MULTI-TIENDA:"
Write-Host "   Frontend:          http://localhost:80" -ForegroundColor White
Write-Host "   Backend API:       http://localhost:8000" -ForegroundColor White
Write-Host "   Health Check:      http://localhost:8000/api/v1/health" -ForegroundColor White
Write-Host "   Stores API:        http://localhost:8000/api/v1/stores" -ForegroundColor White
Write-Host "   API Docs:          http://localhost:8000/docs" -ForegroundColor White

Write-Host ""
Show-Info "CREDENCIALES ENTERPRISE MULTI-TIENDA:"
Write-Host "   SuperAdmin:       superadmin / SuperAdmin123!" -ForegroundColor White
Write-Host "   Tech Admin:       techadmin / TechAdmin123!" -ForegroundColor White
Write-Host "   Business Owner:   businessowner / BusinessOwner123!" -ForegroundColor White
Write-Host "   Global Admin:     globaladmin / Global123!" -ForegroundColor White
Write-Host "   Store Admin:      storeadmin1 / Store123!" -ForegroundColor White

Write-Host ""
Show-Info "TIENDAS CONFIGURADAS:"
Write-Host "   SAB001 - Sabrositas Centro (Sede Principal)" -ForegroundColor White
Write-Host "   SAB002 - Sabrositas Zona Rosa" -ForegroundColor White
Write-Host "   SAB003 - Sabrositas Unicentro" -ForegroundColor White
Write-Host "   SAB004 - Sabrositas Suba" -ForegroundColor White
Write-Host "   SABW01 - Warehouse Centro Logistico" -ForegroundColor White

Write-Host ""
Show-Info "MONITOREO Y ADMINISTRACION:"
Write-Host "   Grafana:           http://localhost:3000" -ForegroundColor White
Write-Host "   Prometheus:        http://localhost:9090" -ForegroundColor White
Write-Host "   Logs:              docker-compose -f docker-compose.production.yml logs -f" -ForegroundColor White
Write-Host "   PostgreSQL:        localhost:5432 (pos_odata)" -ForegroundColor White
Write-Host "   Redis:             localhost:6379" -ForegroundColor White

Write-Host ""
Show-Info "COMANDOS UTILES DE PRODUCCION:"
Write-Host "   Ver logs:             docker-compose -f docker-compose.production.yml logs -f" -ForegroundColor White
Write-Host "   Reiniciar:            docker-compose -f docker-compose.production.yml restart" -ForegroundColor White
Write-Host "   Detener:              docker-compose -f docker-compose.production.yml down" -ForegroundColor White
Write-Host "   Estado:               docker-compose -f docker-compose.production.yml ps" -ForegroundColor White
Write-Host "   Backup DB:            docker exec pos-postgres-production pg_dump -U pos_user pos_odata > backup.sql" -ForegroundColor White

Write-Host ""
Show-Info "CARACTERISTICAS ENTERPRISE IMPLEMENTADAS:"
Write-Host "   Control de acceso multi-tienda por roles" -ForegroundColor Green
Write-Host "   Base de datos PostgreSQL con auditoria" -ForegroundColor Green
Write-Host "   Cache Redis para optimizacion" -ForegroundColor Green
Write-Host "   Nginx como proxy reverso con SSL" -ForegroundColor Green
Write-Host "   Monitoreo con Prometheus + Grafana" -ForegroundColor Green
Write-Host "   Backup automatico de base de datos" -ForegroundColor Green
Write-Host "   Logging estructurado y auditoria" -ForegroundColor Green
Write-Host "   Rate limiting y seguridad avanzada" -ForegroundColor Green

Write-Host ""
Write-Host "SISTEMA MULTI-TIENDA LISTO PARA PRODUCCION!" -ForegroundColor Green
Write-Host "Listo para vender Las Arepas Cuadradas en multiples ubicaciones!" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Green
