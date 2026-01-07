# Script de Inicio Docker - Sistema POS Sabrositas
# ================================================
# Script PowerShell para iniciar el sistema con Docker

Write-Host "[INFO] INICIANDO SISTEMA POS SABROSITAS CON DOCKER" -ForegroundColor Green
Write-Host "=" * 60

# Validar archivo de entorno
if (-not (Test-Path ".env")) {
    Write-Host "❌ Falta .env en el directorio raíz. Copia env.example y configura variables antes de continuar." -ForegroundColor Red
    exit 1
}

# Verificar Docker
try {
    $dockerVersion = docker --version
    Write-Host "✅ Docker: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Docker no encontrado" -ForegroundColor Red
    Write-Host "   Instala Docker Desktop desde https://docker.com" -ForegroundColor Yellow
    exit 1
}

# Verificar Docker Compose
try {
    $composeVersion = docker compose version
    Write-Host "✅ Docker Compose: $composeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Docker Compose no encontrado" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[INFO] Configuración del Sistema:" -ForegroundColor Cyan
Write-Host "   Backend: Python 3.13 + Flask"
Write-Host "   Base de datos: SQLite"
Write-Host "   Redis: Cache y Rate Limiting"
Write-Host "   Puerto: 8000"
Write-Host ""

# Limpiar contenedores anteriores
Write-Host "[INFO] Limpiando contenedores anteriores..." -ForegroundColor Yellow
docker compose down --remove-orphans 2>$null

# Ejecutar test rápido si existen tests básicos
if (Test-Path "tests\test_basic.py") {
    Write-Host "[INFO] Ejecutando tests rápidos antes del build..." -ForegroundColor Yellow
    python -m pytest tests/test_basic.py -q
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Tests fallaron, deteniendo despliegue" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

# Construir e iniciar servicios
Write-Host "[INFO] Construyendo imagen Docker..." -ForegroundColor Yellow
docker compose build --no-cache

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error construyendo la imagen" -ForegroundColor Red
    exit 1
}

Write-Host "[INFO] Iniciando servicios..." -ForegroundColor Yellow
docker compose up -d

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error iniciando servicios" -ForegroundColor Red
    exit 1
}

# Esperar a que el servicio esté listo
Write-Host "[INFO] Esperando que el servicio esté listo..." -ForegroundColor Yellow
$timeout = 60
$elapsed = 0

do {
    Start-Sleep -Seconds 2
    $elapsed += 2
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing -TimeoutSec 3
        if ($response.StatusCode -eq 200) {
            Write-Host "[OK] Servicio listo!" -ForegroundColor Green
            break
        }
    } catch {
        Write-Host "." -NoNewline -ForegroundColor Yellow
    }
} while ($elapsed -lt $timeout)

if ($elapsed -ge $timeout) {
    Write-Host ""
    Write-Host "ERROR: Timeout esperando el servicio" -ForegroundColor Red
    Write-Host "   Verifica los logs: docker compose logs" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "=" * 60
Write-Host "[OK] SISTEMA SABROSITAS INICIADO EXITOSAMENTE" -ForegroundColor Green
Write-Host "=" * 60
Write-Host ""
Write-Host "URLs del Sistema:" -ForegroundColor Cyan
Write-Host "   API Backend: http://localhost:8000" -ForegroundColor White
Write-Host "   Health Check: http://localhost:8000/api/v1/health" -ForegroundColor White
Write-Host ""
Write-Host "Credenciales del Sistema:" -ForegroundColor Cyan
Write-Host "   SuperAdmin:    superadmin / SuperAdmin123!" -ForegroundColor White
Write-Host "   Global Admin:  globaladmin / Global123!" -ForegroundColor White
Write-Host "   Store Admin:   storeadmin1 / Store123!" -ForegroundColor White
Write-Host "   Tech Admin:    techadmin / TechAdmin123!" -ForegroundColor White
Write-Host ""
Write-Host "Comandos Docker útiles:" -ForegroundColor Cyan
Write-Host "   Ver logs:      docker compose logs -f" -ForegroundColor White
Write-Host "   Detener:       docker compose down" -ForegroundColor White
Write-Host "   Reiniciar:     docker compose restart" -ForegroundColor White
Write-Host "   Estado:        docker compose ps" -ForegroundColor White
Write-Host ""
Write-Host "Sistema listo para vender Arepas Cuadradas" -ForegroundColor Green
Write-Host ""

# Abrir navegador
$openBrowser = Read-Host "¿Abrir navegador? (s/N)"
if ($openBrowser -eq "s" -or $openBrowser -eq "S") {
    Start-Process "http://localhost:8000/api/v1/health"
}

Write-Host "Script completado exitosamente" -ForegroundColor Green
