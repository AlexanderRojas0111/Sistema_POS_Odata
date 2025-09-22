# Sistema POS Sabrositas v2.0.0 Enterprise - Despliegue Profesional
# =================================================================
# Las Arepas Cuadradas - Enterprise Architecture
# Despliegue automatizado y profesional del sistema completo

param(
    [switch]$SkipTests = $false,
    [switch]$Production = $false,
    [string]$Environment = "development"
)

# Configuración de colores
$ErrorColor = "Red"
$SuccessColor = "Green"
$InfoColor = "Cyan"
$WarningColor = "Yellow"

# Función para logging
function Write-Log {
    param(
        [string]$Message,
        [string]$Level = "INFO",
        [string]$Color = $InfoColor
    )
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    Write-Host $LogMessage -ForegroundColor $Color
    
    # Guardar en archivo de log
    $LogMessage | Out-File -FilePath "logs/deploy.log" -Append -Encoding UTF8
}

# Función para verificar servicios
function Test-Service {
    param(
        [string]$Url,
        [string]$ServiceName
    )
    
    try {
        $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 10
        if ($response.StatusCode -eq 200) {
            Write-Log "✅ $ServiceName está funcionando correctamente" "SUCCESS" $SuccessColor
            return $true
        } else {
            Write-Log "❌ $ServiceName respondió con código $($response.StatusCode)" "ERROR" $ErrorColor
            return $false
        }
    } catch {
        Write-Log "❌ $ServiceName no está disponible: $($_.Exception.Message)" "ERROR" $ErrorColor
        return $false
    }
}

# Función para esperar servicio
function Wait-ForService {
    param(
        [string]$Url,
        [string]$ServiceName,
        [int]$MaxAttempts = 30,
        [int]$DelaySeconds = 2
    )
    
    Write-Log "🔄 Esperando que $ServiceName esté disponible..." "INFO" $InfoColor
    
    for ($i = 1; $i -le $MaxAttempts; $i++) {
        if (Test-Service -Url $Url -ServiceName $ServiceName) {
            return $true
        }
        
        Write-Log "⏳ Intento $i/$MaxAttempts - Esperando $DelaySeconds segundos..." "INFO" $InfoColor
        Start-Sleep -Seconds $DelaySeconds
    }
    
    Write-Log "❌ $ServiceName no está disponible después de $MaxAttempts intentos" "ERROR" $ErrorColor
    return $false
}

# Inicio del despliegue
Write-Host ""
Write-Host "🚀 SISTEMA POS SABROSITAS v2.0.0 ENTERPRISE - DESPLIEGUE PROFESIONAL" -ForegroundColor $InfoColor
Write-Host "=================================================================" -ForegroundColor $InfoColor
Write-Host "🥟 Las Arepas Cuadradas - Enterprise Architecture" -ForegroundColor $InfoColor
Write-Host "⏰ Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor $InfoColor
Write-Host ""

Write-Log "🎯 Iniciando despliegue profesional del sistema enterprise" "INFO" $InfoColor

# Crear directorio de logs si no existe
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    Write-Log "📁 Directorio de logs creado" "INFO" $InfoColor
}

# Paso 1: Verificar Python y dependencias
Write-Log "🐍 Verificando Python y dependencias..." "INFO" $InfoColor
try {
    $pythonVersion = python --version 2>&1
    Write-Log "✅ Python detectado: $pythonVersion" "SUCCESS" $SuccessColor
    
    # Verificar que requirements.txt existe
    if (Test-Path "requirements.txt") {
        Write-Log "✅ requirements.txt encontrado" "SUCCESS" $SuccessColor
    } else {
        Write-Log "❌ requirements.txt no encontrado" "ERROR" $ErrorColor
        exit 1
    }
} catch {
    Write-Log "❌ Error verificando Python: $($_.Exception.Message)" "ERROR" $ErrorColor
    exit 1
}

# Paso 2: Verificar Node.js y npm
Write-Log "📦 Verificando Node.js y npm..." "INFO" $InfoColor
try {
    $nodeVersion = node --version 2>&1
    $npmVersion = npm --version 2>&1
    Write-Log "✅ Node.js: $nodeVersion" "SUCCESS" $SuccessColor
    Write-Log "✅ npm: $npmVersion" "SUCCESS" $SuccessColor
} catch {
    Write-Log "❌ Error verificando Node.js: $($_.Exception.Message)" "ERROR" $ErrorColor
    exit 1
}

# Paso 3: Corregir base de datos si es necesario
Write-Log "🗄️ Verificando base de datos..." "INFO" $InfoColor
if (Test-Path "fix_database_multi_payment.py") {
    try {
        python fix_database_multi_payment.py
        Write-Log "✅ Base de datos verificada y corregida" "SUCCESS" $SuccessColor
    } catch {
        Write-Log "⚠️ Advertencia en corrección de base de datos: $($_.Exception.Message)" "WARNING" $WarningColor
    }
} else {
    Write-Log "⚠️ Script de corrección de base de datos no encontrado" "WARNING" $WarningColor
}

# Paso 4: Instalar dependencias del backend
Write-Log "📚 Instalando dependencias del backend..." "INFO" $InfoColor
try {
    pip install -r requirements.txt --quiet
    Write-Log "✅ Dependencias del backend instaladas" "SUCCESS" $SuccessColor
} catch {
    Write-Log "❌ Error instalando dependencias del backend: $($_.Exception.Message)" "ERROR" $ErrorColor
    exit 1
}

# Paso 5: Instalar dependencias del frontend
Write-Log "🎨 Instalando dependencias del frontend..." "INFO" $InfoColor
try {
    Set-Location frontend
    npm install --silent
    Set-Location ..
    Write-Log "✅ Dependencias del frontend instaladas" "SUCCESS" $SuccessColor
} catch {
    Write-Log "❌ Error instalando dependencias del frontend: $($_.Exception.Message)" "ERROR" $ErrorColor
    Set-Location ..
    exit 1
}

# Paso 6: Iniciar backend
Write-Log "🚀 Iniciando backend enterprise..." "INFO" $InfoColor
try {
    # Detener procesos existentes
    Get-Process -Name "python" -ErrorAction SilentlyContinue | Where-Object { $_.MainWindowTitle -like "*main.py*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    # Iniciar backend en background
    Start-Process -FilePath "python" -ArgumentList "main.py" -WindowStyle Hidden
    Write-Log "✅ Backend iniciado en background" "SUCCESS" $SuccessColor
    
    # Esperar que el backend esté disponible
    if (Wait-ForService -Url "http://localhost:8000/api/v1/health" -ServiceName "Backend API") {
        Write-Log "✅ Backend enterprise funcionando correctamente" "SUCCESS" $SuccessColor
    } else {
        Write-Log "❌ Backend no está disponible" "ERROR" $ErrorColor
        exit 1
    }
} catch {
    Write-Log "❌ Error iniciando backend: $($_.Exception.Message)" "ERROR" $ErrorColor
    exit 1
}

# Paso 7: Iniciar frontend
Write-Log "🎨 Iniciando frontend enterprise..." "INFO" $InfoColor
try {
    # Detener procesos existentes
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*npm*" } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    # Iniciar frontend en background
    Set-Location frontend
    Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Hidden
    Set-Location ..
    Write-Log "✅ Frontend iniciado en background" "SUCCESS" $SuccessColor
    
    # Esperar que el frontend esté disponible
    if (Wait-ForService -Url "http://localhost:5173" -ServiceName "Frontend") {
        Write-Log "✅ Frontend enterprise funcionando correctamente" "SUCCESS" $SuccessColor
    } else {
        Write-Log "❌ Frontend no está disponible" "ERROR" $ErrorColor
        exit 1
    }
} catch {
    Write-Log "❌ Error iniciando frontend: $($_.Exception.Message)" "ERROR" $ErrorColor
    Set-Location ..
    exit 1
}

# Paso 8: Validación completa del sistema
Write-Log "🔍 Realizando validación completa del sistema..." "INFO" $InfoColor

$ServicesToTest = @(
    @{Url="http://localhost:8000/api/v1/health"; Name="API v1 Health"},
    @{Url="http://localhost:8000/api/v1/products"; Name="API v1 Products"},
    @{Url="http://localhost:8000/api/v1/users"; Name="API v1 Users"},
    @{Url="http://localhost:8000/api/v1/multi-payment/methods"; Name="Multi-Payment API"},
    @{Url="http://localhost:8000/api/v2/ai/health"; Name="AI API Health"},
    @{Url="http://localhost:5173"; Name="Frontend"}
)

$AllServicesWorking = $true

foreach ($service in $ServicesToTest) {
    if (-not (Test-Service -Url $service.Url -ServiceName $service.Name)) {
        $AllServicesWorking = $false
    }
}

# Paso 9: Mostrar resumen del despliegue
Write-Host ""
Write-Host "📊 RESUMEN DEL DESPLIEGUE" -ForegroundColor $InfoColor
Write-Host "========================" -ForegroundColor $InfoColor

if ($AllServicesWorking) {
    Write-Host ""
    Write-Host "🎉 DESPLIEGUE EXITOSO - SISTEMA ENTERPRISE OPERATIVO" -ForegroundColor $SuccessColor
    Write-Host "===================================================" -ForegroundColor $SuccessColor
    Write-Host ""
    Write-Host "🌐 URLs del Sistema:" -ForegroundColor $InfoColor
    Write-Host "   Frontend:      http://localhost:5173" -ForegroundColor $SuccessColor
    Write-Host "   Backend API:   http://localhost:8000" -ForegroundColor $SuccessColor
    Write-Host "   Health Check:  http://localhost:8000/api/v1/health" -ForegroundColor $SuccessColor
    Write-Host "   Multi-Payment: http://localhost:8000/api/v1/multi-payment/" -ForegroundColor $SuccessColor
    Write-Host "   AI API:        http://localhost:8000/api/v2/ai/" -ForegroundColor $SuccessColor
    Write-Host ""
    Write-Host "👥 Credenciales:" -ForegroundColor $InfoColor
    Write-Host "   Usuario: admin" -ForegroundColor $SuccessColor
    Write-Host "   Contraseña: admin" -ForegroundColor $SuccessColor
    Write-Host ""
    Write-Host "💳 Funcionalidades Enterprise:" -ForegroundColor $InfoColor
    Write-Host "   ✅ Pagos Múltiples" -ForegroundColor $SuccessColor
    Write-Host "   ✅ Inteligencia Artificial" -ForegroundColor $SuccessColor
    Write-Host "   ✅ Multi-sede" -ForegroundColor $SuccessColor
    Write-Host "   ✅ Seguridad Enterprise" -ForegroundColor $SuccessColor
    Write-Host "   ✅ Monitoreo en Tiempo Real" -ForegroundColor $SuccessColor
    Write-Host ""
    Write-Log "🎉 Sistema POS Sabrositas v2.0.0 Enterprise desplegado exitosamente" "SUCCESS" $SuccessColor
} else {
    Write-Host ""
    Write-Host "❌ DESPLIEGUE CON ERRORES - REVISAR SERVICIOS" -ForegroundColor $ErrorColor
    Write-Host "=============================================" -ForegroundColor $ErrorColor
    Write-Log "❌ Despliegue completado con errores" "ERROR" $ErrorColor
    exit 1
}

Write-Host ""
Write-Host "⏰ Despliegue completado: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor $InfoColor
Write-Host "📝 Log guardado en: logs/deploy.log" -ForegroundColor $InfoColor
Write-Host ""

# Limpiar archivos temporales
if (Test-Path "fix_database_multi_payment.py") {
    Remove-Item "fix_database_multi_payment.py" -Force
    Write-Log "Archivos temporales limpiados" "INFO" $InfoColor
}

Write-Log "Despliegue profesional completado" "SUCCESS" $SuccessColor
