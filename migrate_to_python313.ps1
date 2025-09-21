# Script de Migración a Python 3.13 - Sistema POS Sabrositas v2.0.0
# ====================================================================

param(
    [switch]$SkipBackup,
    [switch]$ForceInstall,
    [string]$PythonPath = "python3.13"
)

Write-Host "🐍 MIGRACIÓN A PYTHON 3.13 - SISTEMA POS SABROSITAS v2.0.0" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green
Write-Host "🥟 Las Arepas Cuadradas - Actualización Enterprise" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Green

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
Show-Info "FASE 1: VALIDACIÓN DE PYTHON 3.13"
Write-Host ""

# Verificar Python 3.13
try {
    $python313Version = & $PythonPath --version 2>&1
    if ($python313Version -match "Python 3\.13") {
        Show-Success "Python 3.13 encontrado: $python313Version"
    } else {
        Show-Error "Python 3.13 no encontrado. Instale Python 3.13 desde python.org"
    }
} catch {
    Show-Error "Python 3.13 no encontrado. Instale desde: https://www.python.org/downloads/"
}

Write-Host ""
Show-Info "FASE 2: BACKUP DEL SISTEMA ACTUAL"
Write-Host ""

if (-not $SkipBackup) {
    # Backup de base de datos
    if (Test-Path "instance\pos_odata.db") {
        $backupTimestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        Copy-Item "instance\pos_odata.db" "instance\pos_odata_python39_backup_$backupTimestamp.db"
        Show-Success "Backup de base de datos creado: pos_odata_python39_backup_$backupTimestamp.db"
    }
    
    # Backup de entorno virtual actual
    if (Test-Path "venv_python313") {
        Rename-Item "venv_python313" "venv_python39_backup_$backupTimestamp"
        Show-Success "Backup de entorno virtual creado"
    }
} else {
    Show-Warning "Backup omitido (--SkipBackup especificado)"
}

Write-Host ""
Show-Info "FASE 3: CREACIÓN DE ENTORNO PYTHON 3.13"
Write-Host ""

# Crear nuevo entorno virtual
try {
    Show-Info "Creando entorno virtual Python 3.13..."
    & $PythonPath -m venv venv_python313_new
    Show-Success "Entorno virtual Python 3.13 creado"
} catch {
    Show-Error "Error creando entorno virtual Python 3.13"
}

# Activar entorno virtual
Show-Info "Activando entorno virtual Python 3.13..."
try {
    & ".\venv_python313_new\Scripts\Activate.ps1"
    Show-Success "Entorno virtual activado"
} catch {
    Show-Warning "Error activando entorno - continúe manualmente"
}

Write-Host ""
Show-Info "FASE 4: INSTALACIÓN DE DEPENDENCIAS ACTUALIZADAS"
Write-Host ""

# Actualizar pip
Show-Info "Actualizando pip, setuptools y wheel..."
try {
    & ".\venv_python313_new\Scripts\python.exe" -m pip install --upgrade pip setuptools wheel
    Show-Success "Herramientas base actualizadas"
} catch {
    Show-Error "Error actualizando herramientas base"
}

# Instalar dependencias
Show-Info "Instalando dependencias optimizadas para Python 3.13..."
try {
    & ".\venv_python313_new\Scripts\python.exe" -m pip install -r requirements-python313.txt
    Show-Success "Dependencias Python 3.13 instaladas"
} catch {
    Show-Error "Error instalando dependencias Python 3.13"
}

Write-Host ""
Show-Info "FASE 5: INICIALIZACIÓN DEL SISTEMA"
Write-Host ""

# Inicializar sistema con Python 3.13
Show-Info "Inicializando sistema con Python 3.13..."
try {
    & ".\venv_python313_new\Scripts\python.exe" initialize_complete_system.py
    Show-Success "Sistema inicializado con Python 3.13"
} catch {
    Show-Warning "Error en inicialización automática - puede requerir intervención manual"
}

Write-Host ""
Show-Info "FASE 6: VALIDACIÓN DEL SISTEMA MIGRADO"
Write-Host ""

# Validar librerías principales
Show-Info "Validando librerías principales..."
try {
    $testResult = & ".\venv_python313_new\Scripts\python.exe" -c "import flask, sqlalchemy, sklearn, numpy; print('OK')"
    if ($testResult -eq "OK") {
        Show-Success "Librerías principales funcionando"
    } else {
        Show-Warning "Problemas con librerías principales"
    }
} catch {
    Show-Warning "Error validando librerías principales"
}

# Validar sistema de IA
Show-Info "Validando sistema de IA..."
try {
    $aiTestResult = & ".\venv_python313_new\Scripts\python.exe" -c "from app.services.ai_service import AIService; print('OK')"
    if ($aiTestResult -eq "OK") {
        Show-Success "Sistema de IA funcionando"
    } else {
        Show-Warning "Problemas con sistema de IA"
    }
} catch {
    Show-Warning "Error validando sistema de IA"
}

Write-Host ""
Show-Info "FASE 7: FINALIZACIÓN DE MIGRACIÓN"
Write-Host ""

# Renombrar entornos
if (Test-Path "venv_python313_new") {
    if (Test-Path "venv_python313") {
        Remove-Item "venv_python313" -Recurse -Force
    }
    Rename-Item "venv_python313_new" "venv_python313"
    Show-Success "Entorno Python 3.13 configurado como principal"
}

Write-Host ""
Write-Host "🎉 MIGRACIÓN A PYTHON 3.13 COMPLETADA" -ForegroundColor Green
Write-Host "=================================================================" -ForegroundColor Green

Write-Host ""
Show-Info "COMANDOS PARA USAR EL SISTEMA MIGRADO:"
Write-Host "   Activar entorno:    .\venv_python313\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "   Verificar versión:  python --version" -ForegroundColor White
Write-Host "   Iniciar backend:    python main.py" -ForegroundColor White
Write-Host "   Iniciar frontend:   cd frontend && npm run dev" -ForegroundColor White

Write-Host ""
Show-Info "VERIFICACIÓN FINAL:"
Write-Host "   Frontend:           http://localhost:5173" -ForegroundColor White
Write-Host "   Backend:            http://localhost:8000" -ForegroundColor White
Write-Host "   Health Check:       http://localhost:8000/api/v1/health" -ForegroundColor White

Write-Host ""
Show-Info "CREDENCIALES (sin cambios):"
Write-Host "   SuperAdmin:         superadmin / SuperAdmin123!" -ForegroundColor White
Write-Host "   Global Admin:       globaladmin / Global123!" -ForegroundColor White

Write-Host ""
Write-Host "🚀 ¡SISTEMA SABROSITAS ACTUALIZADO A PYTHON 3.13!" -ForegroundColor Green
Write-Host "🥟 ¡Listo para vender Arepas Cuadradas con la última tecnología!" -ForegroundColor Yellow
Write-Host "=================================================================" -ForegroundColor Green
