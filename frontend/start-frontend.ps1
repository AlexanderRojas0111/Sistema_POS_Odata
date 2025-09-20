# Script de Inicio Frontend - Sabrositas POS
# ==========================================
# Script PowerShell para iniciar frontend de forma robusta

Write-Host "🚀 INICIANDO FRONTEND SABROSITAS POS" -ForegroundColor Green
Write-Host "=" * 50

# Verificar directorio
$currentDir = Get-Location
Write-Host "📁 Directorio actual: $currentDir"

if (-not (Test-Path "package.json")) {
    Write-Host "❌ Error: package.json no encontrado" -ForegroundColor Red
    Write-Host "   Asegúrate de estar en el directorio frontend/" -ForegroundColor Yellow
    exit 1
}

# Verificar Node.js
try {
    $nodeVersion = node --version
    Write-Host "✅ Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: Node.js no encontrado" -ForegroundColor Red
    Write-Host "   Instala Node.js desde https://nodejs.org" -ForegroundColor Yellow
    exit 1
}

# Verificar NPM
try {
    $npmVersion = npm --version
    Write-Host "✅ NPM: v$npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Error: NPM no encontrado" -ForegroundColor Red
    exit 1
}

# Verificar dependencias
if (-not (Test-Path "node_modules")) {
    Write-Host "📦 Instalando dependencias..." -ForegroundColor Yellow
    npm install
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error instalando dependencias" -ForegroundColor Red
        exit 1
    }
}

# Limpiar procesos anteriores
Write-Host "🧹 Limpiando procesos Node.js anteriores..." -ForegroundColor Yellow
Get-Process node -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Verificar puerto 5173
$portInUse = Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "⚠️  Puerto 5173 en uso, liberando..." -ForegroundColor Yellow
    $processId = $portInUse.OwningProcess
    Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
    Start-Sleep 2
}

# Configurar variables de entorno
$env:VITE_API_URL = "http://localhost:8000"
$env:VITE_APP_NAME = "Sabrositas POS"
$env:VITE_MULTISTORE_ENABLED = "true"

Write-Host "🔧 Variables de entorno configuradas:" -ForegroundColor Cyan
Write-Host "   VITE_API_URL: $env:VITE_API_URL"
Write-Host "   VITE_APP_NAME: $env:VITE_APP_NAME"
Write-Host "   VITE_MULTISTORE_ENABLED: $env:VITE_MULTISTORE_ENABLED"

# Verificar backend disponible
Write-Host "🔍 Verificando backend..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ Backend disponible en puerto 8000" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Backend responde con código: $($response.StatusCode)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Backend no disponible en puerto 8000" -ForegroundColor Red
    Write-Host "   Inicia el backend primero: python main.py" -ForegroundColor Yellow
}

Write-Host "`n🚀 Iniciando servidor Vite..." -ForegroundColor Green
Write-Host "📱 Frontend estará disponible en: http://localhost:5173" -ForegroundColor Cyan
Write-Host "🌐 Network access: http://[tu-ip]:5173" -ForegroundColor Cyan
Write-Host "`n💡 Para detener: Ctrl+C" -ForegroundColor Yellow
Write-Host "=" * 50

# Iniciar Vite
npm run dev
