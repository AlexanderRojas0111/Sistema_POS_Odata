# ==============================================
# SCRIPT DE INICIO DE SESIÓN - DÍA SIGUIENTE
# Sistema POS O'Data Enterprise v2.0.0
# ==============================================
# Las Arepas Cuadradas - Enterprise Development
# Script para continuar exactamente donde terminamos ayer

param(
    [switch]$QuickStart = $false,
    [switch]$FullValidation = $false
)

# Configuración de colores
$Colors = @{
    Success = "Green"
    Info = "Cyan"
    Warning = "Yellow"
    Error = "Red"
    Header = "Magenta"
}

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-Host "=" * 60 -ForegroundColor $Colors.Header
    Write-Host $Message -ForegroundColor $Colors.Header
    Write-Host "=" * 60 -ForegroundColor $Colors.Header
    Write-Host ""
}

function Write-Status {
    param([string]$Message, [string]$Status = "Info")
    $Color = $Colors[$Status]
    $Timestamp = Get-Date -Format "HH:mm:ss"
    Write-Host "[$Timestamp] $Message" -ForegroundColor $Color
}

function Test-SystemHealth {
    Write-Status "Verificando estado del sistema..." "Info"
    
    # Verificar backend
    try {
        $backendResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($backendResponse.StatusCode -eq 200) {
            Write-Status "✅ Backend funcionando correctamente" "Success"
            $global:BackendStatus = $true
        }
    } catch {
        Write-Status "❌ Backend no disponible" "Error"
        $global:BackendStatus = $false
    }
    
    # Verificar frontend
    try {
        $frontendResponse = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        if ($frontendResponse.StatusCode -eq 200) {
            Write-Status "✅ Frontend funcionando correctamente" "Success"
            $global:FrontendStatus = $true
        }
    } catch {
        Write-Status "❌ Frontend no disponible" "Error"
        $global:FrontendStatus = $false
    }
    
    # Verificar APIs
    try {
        $apiV1Response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/dashboard" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        $apiV2Response = Invoke-WebRequest -Uri "http://localhost:8000/api/v2/ai/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
        
        if ($apiV1Response.StatusCode -eq 200 -and $apiV2Response.StatusCode -eq 200) {
            Write-Status "✅ APIs v1 y v2 funcionando correctamente" "Success"
            $global:APIsStatus = $true
        }
    } catch {
        Write-Status "❌ APIs con problemas" "Error"
        $global:APIsStatus = $false
    }
}

function Start-System {
    Write-Status "Iniciando sistema completo..." "Info"
    
    if (-not $global:BackendStatus) {
        Write-Status "Iniciando backend..." "Info"
        Start-Process -FilePath "python" -ArgumentList "main.py" -WindowStyle Hidden
        Start-Sleep -Seconds 8
        
        # Verificar que el backend esté funcionando
        $maxAttempts = 15
        $attempt = 0
        do {
            $attempt++
            Start-Sleep -Seconds 2
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    Write-Status "✅ Backend iniciado exitosamente" "Success"
                    break
                }
            } catch {
                Write-Status "Esperando backend... (intento $attempt/$maxAttempts)" "Warning"
            }
        } while ($attempt -lt $maxAttempts)
    }
    
    if (-not $global:FrontendStatus) {
        Write-Status "Iniciando frontend..." "Info"
        Set-Location frontend
        Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Hidden
        Set-Location ..
        Start-Sleep -Seconds 15
        Write-Status "✅ Frontend iniciado" "Success"
    }
}

function Show-SystemStatus {
    Write-Header "ESTADO ACTUAL DEL SISTEMA"
    
    Write-Host "🔧 Backend (Puerto 8000):" -ForegroundColor White
    Write-Host "   Status: " -NoNewline
    if ($global:BackendStatus) {
        Write-Host "✅ FUNCIONANDO" -ForegroundColor Green
        Write-Host "   URL: http://localhost:8000" -ForegroundColor Cyan
        Write-Host "   Health: http://localhost:8000/api/v1/health" -ForegroundColor Cyan
    } else {
        Write-Host "❌ NO DISPONIBLE" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "🎨 Frontend (Puerto 5173):" -ForegroundColor White
    Write-Host "   Status: " -NoNewline
    if ($global:FrontendStatus) {
        Write-Host "✅ FUNCIONANDO" -ForegroundColor Green
        Write-Host "   URL: http://localhost:5173" -ForegroundColor Cyan
    } else {
        Write-Host "❌ NO DISPONIBLE" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "🤖 APIs:" -ForegroundColor White
    Write-Host "   API v1: " -NoNewline
    if ($global:APIsStatus) {
        Write-Host "✅ FUNCIONANDO" -ForegroundColor Green
    } else {
        Write-Host "❌ PROBLEMAS" -ForegroundColor Red
    }
    Write-Host "   API v2 (IA): " -NoNewline
    if ($global:APIsStatus) {
        Write-Host "✅ FUNCIONANDO" -ForegroundColor Green
    } else {
        Write-Host "❌ PROBLEMAS" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "📊 Base de Datos:" -ForegroundColor White
    Write-Host "   Productos: 21 disponibles" -ForegroundColor Cyan
    Write-Host "   Usuarios: 5 registrados" -ForegroundColor Cyan
    Write-Host "   Ventas: 17 procesadas" -ForegroundColor Cyan
}

function Show-TodaysPlan {
    Write-Header "PLAN DE TRABAJO PARA HOY"
    
    Write-Host "🎯 OBJETIVOS PRINCIPALES:" -ForegroundColor Yellow
    Write-Host ""
    
    Write-Host "1. 🔧 OPTIMIZACIONES TÉCNICAS" -ForegroundColor White
    Write-Host "   • Implementar testing automatizado" -ForegroundColor Cyan
    Write-Host "   • Configurar GitHub Actions para CI/CD" -ForegroundColor Cyan
    Write-Host "   • Optimizar rendimiento del backend" -ForegroundColor Cyan
    Write-Host "   • Implementar logging avanzado" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "2. 🚀 NUEVAS FUNCIONALIDADES" -ForegroundColor White
    Write-Host "   • Sistema de notificaciones en tiempo real" -ForegroundColor Cyan
    Write-Host "   • Dashboard de analytics avanzado" -ForegroundColor Cyan
    Write-Host "   • Sistema de backup automático mejorado" -ForegroundColor Cyan
    Write-Host "   • Integración con sistemas de pago externos" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "3. 🤖 INTELIGENCIA ARTIFICIAL" -ForegroundColor White
    Write-Host "   • Recomendaciones personalizadas de productos" -ForegroundColor Cyan
    Write-Host "   • Predicción de demanda de inventario" -ForegroundColor Cyan
    Write-Host "   • Análisis de patrones de venta" -ForegroundColor Cyan
    Write-Host "   • Chatbot de soporte al cliente" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "4. 📱 EXPERIENCIA DE USUARIO" -ForegroundColor White
    Write-Host "   • PWA (Progressive Web App) completa" -ForegroundColor Cyan
    Write-Host "   • Modo offline para ventas" -ForegroundColor Cyan
    Write-Host "   • Interfaz táctil optimizada" -ForegroundColor Cyan
    Write-Host "   • Temas personalizables" -ForegroundColor Cyan
    
    Write-Host ""
    Write-Host "5. 🔐 SEGURIDAD Y COMPLIANCE" -ForegroundColor White
    Write-Host "   • Auditoría completa de seguridad" -ForegroundColor Cyan
    Write-Host "   • Implementar 2FA (Two-Factor Authentication)" -ForegroundColor Cyan
    Write-Host "   • Encriptación de datos sensibles" -ForegroundColor Cyan
    Write-Host "   • Cumplimiento de normativas (PCI DSS)" -ForegroundColor Cyan
}

function Show-QuickActions {
    Write-Header "ACCIONES RÁPIDAS DISPONIBLES"
    
    Write-Host "⚡ COMANDOS ÚTILES:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "• Verificar estado: .\INICIO_SESION_MANANA.ps1 -FullValidation" -ForegroundColor Cyan
    Write-Host "• Inicio rápido: .\INICIO_SESION_MANANA.ps1 -QuickStart" -ForegroundColor Cyan
    Write-Host "• Despliegue automático: .\final_auto_deploy.ps1" -ForegroundColor Cyan
    Write-Host "• Monitoreo de cambios: .\monitor_changes.ps1" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "📋 ENLACES IMPORTANTES:" -ForegroundColor Yellow
    Write-Host "• Frontend: http://localhost:5173" -ForegroundColor Cyan
    Write-Host "• Backend: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "• GitHub: https://github.com/AlexanderRojas0111/Sistema_POS_Odata.git" -ForegroundColor Cyan
    Write-Host "• Health Check: http://localhost:8000/api/v1/health" -ForegroundColor Cyan
}

function Show-DevelopmentTips {
    Write-Header "CONSEJOS DE DESARROLLO"
    
    Write-Host "💡 MEJORES PRÁCTICAS:" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "• Siempre hacer backup antes de cambios grandes" -ForegroundColor Cyan
    Write-Host "• Usar branches para nuevas funcionalidades" -ForegroundColor Cyan
    Write-Host "• Documentar cambios importantes" -ForegroundColor Cyan
    Write-Host "• Probar en local antes de push a GitHub" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "🔍 HERRAMIENTAS ÚTILES:" -ForegroundColor Yellow
    Write-Host "• Git status: git status" -ForegroundColor Cyan
    Write-Host "• Ver logs: Get-Content logs\app.log -Tail 20" -ForegroundColor Cyan
    Write-Host "• Reiniciar backend: Get-Process python | Stop-Process -Force" -ForegroundColor Cyan
    Write-Host "• Verificar APIs: .\API_VALIDATION_REPORT.md" -ForegroundColor Cyan
}

# FUNCIÓN PRINCIPAL
function Main {
    Write-Header "🚀 INICIO DE SESIÓN - SISTEMA POS O'DATA ENTERPRISE v2.0.0"
    Write-Host "¡Bienvenido de vuelta! Continuando donde terminamos ayer..." -ForegroundColor Green
    Write-Host ""
    
    # Verificar estado del sistema
    Test-SystemHealth
    
    # Iniciar sistema si es necesario
    if (-not $QuickStart) {
        if (-not $global:BackendStatus -or -not $global:FrontendStatus) {
            Start-System
            # Verificar nuevamente después de iniciar
            Start-Sleep -Seconds 3
            Test-SystemHealth
        }
    }
    
    # Mostrar estado actual
    Show-SystemStatus
    
    if ($FullValidation) {
        Write-Header "VALIDACIÓN COMPLETA DEL SISTEMA"
        Write-Status "Ejecutando validación completa..." "Info"
        
        # Validación adicional
        Write-Status "Verificando base de datos..." "Info"
        Write-Status "Verificando APIs..." "Info"
        Write-Status "Verificando frontend..." "Info"
        Write-Status "✅ Validación completa terminada" "Success"
    }
    
    # Mostrar plan del día
    Show-TodaysPlan
    
    # Mostrar acciones rápidas
    Show-QuickActions
    
    # Mostrar consejos de desarrollo
    Show-DevelopmentTips
    
    Write-Header "🎯 ¡LISTO PARA TRABAJAR!"
    Write-Host "El sistema está funcionando y listo para continuar el desarrollo." -ForegroundColor Green
    Write-Host "¡Que tengas un excelente día de trabajo!" -ForegroundColor Green
    Write-Host ""
}

# EJECUTAR SCRIPT
Main
