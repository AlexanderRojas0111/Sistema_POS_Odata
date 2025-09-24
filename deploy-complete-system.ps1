# 🚀 DESPLIEGUE COMPLETO DEL SISTEMA POS SABROSITAS v2.0.0
# =============================================================
# Las Arepas Cuadradas - Enterprise Edition con Python 3.13
# =============================================================

param(
    [switch]$SkipBackend,
    [switch]$SkipFrontend,
    [switch]$Production
)

Write-Host "🚀 DESPLIEGUE COMPLETO DEL SISTEMA POS SABROSITAS" -ForegroundColor Green
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host "Las Arepas Cuadradas - Enterprise Edition" -ForegroundColor Yellow
Write-Host "Python 3.13.7 + React + TypeScript" -ForegroundColor Yellow
Write-Host "=============================================================" -ForegroundColor Cyan

# Función para mostrar información
function Show-Info {
    param($Message, $Color = "Green")
    Write-Host "✅ $Message" -ForegroundColor $Color
}

function Show-Warning {
    param($Message)
    Write-Host "⚠️ $Message" -ForegroundColor Yellow
}

function Show-Error {
    param($Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

# Verificar Python 3.13
Write-Host "`n🔍 VERIFICANDO PYTHON 3.13..." -ForegroundColor Cyan
try {
    $pythonVersion = py -3.13 --version
    Show-Info "Python 3.13 detectado: $pythonVersion"
} catch {
    Show-Error "Python 3.13 no está disponible. Instalando..."
    winget install Python.Python.3.13
}

# Verificar Node.js
Write-Host "`n🔍 VERIFICANDO NODE.JS..." -ForegroundColor Cyan
try {
    $nodeVersion = node --version
    Show-Info "Node.js detectado: $nodeVersion"
} catch {
    Show-Error "Node.js no está instalado. Instalando..."
    winget install OpenJS.NodeJS
}

# ACTIVAR ENTORNO VIRTUAL PYTHON 3.13
Write-Host "`n🐍 ACTIVANDO ENTORNO VIRTUAL PYTHON 3.13..." -ForegroundColor Cyan
if (Test-Path "venv_python313") {
    Show-Info "Entorno virtual Python 3.13 encontrado"
    & ".\venv_python313\Scripts\Activate.ps1"
} else {
    Show-Warning "Creando nuevo entorno virtual Python 3.13..."
    py -3.13 -m venv venv_python313
    & ".\venv_python313\Scripts\Activate.ps1"
    pip install -r requirements-python313-core.txt
    pip install numpy pandas nltk scikit-learn scipy qrcode Pillow redis celery
}

# DESPLEGAR BACKEND
if (-not $SkipBackend) {
    Write-Host "`n🔧 DESPLEGANDO BACKEND..." -ForegroundColor Cyan
    Show-Info "Iniciando backend en puerto 8000..."
    
    # Verificar si el backend ya está ejecutándose
    $backendProcess = Get-Process python* -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*main.py*" }
    if ($backendProcess) {
        Show-Warning "Backend ya está ejecutándose. Deteniendo proceso anterior..."
        $backendProcess | Stop-Process -Force
    }
    
    # Iniciar backend en segundo plano
    Start-Process powershell -ArgumentList "-Command", ".\venv_python313\Scripts\Activate.ps1; python main.py" -WindowStyle Hidden
    
    # Esperar a que el backend inicie
    Start-Sleep -Seconds 10
    
    # Verificar que el backend esté funcionando
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Show-Info "Backend funcionando correctamente en puerto 8000"
        }
    } catch {
        Show-Warning "Backend no responde inmediatamente, pero debería estar iniciando..."
    }
}

# DESPLEGAR FRONTEND
if (-not $SkipFrontend) {
    Write-Host "`n🎨 DESPLEGANDO FRONTEND..." -ForegroundColor Cyan
    Set-Location "frontend"
    
    # Verificar dependencias
    if (!(Test-Path "node_modules")) {
        Show-Info "Instalando dependencias del frontend..."
        npm install
    }
    
    # Construir para producción
    if ($Production) {
        Show-Info "Construyendo frontend para producción..."
        npm run build:production
        Show-Info "Iniciando servidor de preview en puerto 4173..."
        Start-Process powershell -ArgumentList "-Command", "npm run preview" -WindowStyle Hidden
        $frontendUrl = "http://localhost:4173"
    } else {
        Show-Info "Iniciando servidor de desarrollo en puerto 5173..."
        Start-Process powershell -ArgumentList "-Command", "npm run dev" -WindowStyle Hidden
        $frontendUrl = "http://localhost:5173"
    }
    
    Set-Location ".."
    
    # Esperar a que el frontend inicie
    Start-Sleep -Seconds 15
    
    # Verificar que el frontend esté funcionando
    try {
        $frontendPort = if ($Production) { "4173" } else { "5173" }
        $response = Invoke-WebRequest -Uri "http://localhost:$frontendPort" -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Show-Info "Frontend funcionando correctamente en puerto $frontendPort"
        }
    } catch {
        Show-Warning "Frontend no responde inmediatamente, pero debería estar iniciando..."
    }
}

# VALIDACIÓN FINAL
Write-Host "`n🔍 VALIDACIÓN FINAL DEL SISTEMA..." -ForegroundColor Cyan
try {
    & ".\venv_python313\Scripts\Activate.ps1"
    python scripts/validate_system.py
} catch {
    Show-Warning "No se pudo ejecutar la validación automática"
}

# MOSTRAR RESUMEN
Write-Host "`n🎉 DESPLIEGUE COMPLETADO" -ForegroundColor Green
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host "🌐 Backend: http://localhost:8000" -ForegroundColor Yellow
Write-Host "🎨 Frontend: $frontendUrl" -ForegroundColor Yellow
Write-Host "📊 API Health: http://localhost:8000/api/v1/health" -ForegroundColor Yellow
Write-Host "📈 Dashboard: http://localhost:8000/api/v1/dashboard/summary" -ForegroundColor Yellow
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host "🚀 Sistema POS Sabrositas v2.0.0 Enterprise funcionando!" -ForegroundColor Green
Write-Host "💻 Python 3.13.7 + React + TypeScript" -ForegroundColor Cyan
Write-Host "`n📋 Para detener los servicios:" -ForegroundColor Yellow
Write-Host "   - Backend: Ctrl+C en la ventana del backend" -ForegroundColor White
Write-Host "   - Frontend: Ctrl+C en la ventana del frontend" -ForegroundColor White
Write-Host "   - O ejecutar: Get-Process python*,node* | Stop-Process" -ForegroundColor White
