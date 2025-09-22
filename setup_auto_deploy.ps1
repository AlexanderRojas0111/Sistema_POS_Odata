# ==============================================
# CONFIGURACIÓN DEL SISTEMA DE DESPLIEGUE AUTOMÁTICO
# Sistema POS Sabrositas v2.0.0 Enterprise
# ==============================================

Write-Host "🔧 CONFIGURACIÓN DEL SISTEMA DE DESPLIEGUE AUTOMÁTICO" -ForegroundColor Green
Write-Host "=====================================================" -ForegroundColor Green
Write-Host "🥟 Sistema POS Sabrositas v2.0.0 Enterprise" -ForegroundColor Yellow
Write-Host ""

# Crear directorio de logs si no existe
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    Write-Host "✅ Directorio de logs creado" -ForegroundColor Green
}

# Crear directorio de backups si no existe
if (!(Test-Path "backups")) {
    New-Item -ItemType Directory -Path "backups" -Force | Out-Null
    Write-Host "✅ Directorio de backups creado" -ForegroundColor Green
}

# Crear script de inicio automático
$startupScript = @"
# ==============================================
# INICIO AUTOMÁTICO DEL SISTEMA
# Sistema POS Sabrositas v2.0.0 Enterprise
# ==============================================

# Cambiar al directorio del proyecto
Set-Location "$(Get-Location)"

# Ejecutar despliegue automático
& ".\auto_deploy_system.ps1" -ForceRestart

# Iniciar monitor de actualizaciones en background
Start-Process -FilePath "powershell" -ArgumentList "-File", ".\monitor_updates.ps1" -WindowStyle Hidden

Write-Host "🚀 Sistema POS Sabrositas iniciado automáticamente" -ForegroundColor Green
Write-Host "📊 Monitor de actualizaciones activo" -ForegroundColor Cyan
"@

$startupScript | Out-File -FilePath "start_sabrositas_auto.ps1" -Encoding UTF8
Write-Host "✅ Script de inicio automático creado: start_sabrositas_auto.ps1" -ForegroundColor Green

# Crear tarea programada (opcional)
$taskName = "SabrositasAutoDeploy"
$taskExists = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

if ($taskExists) {
    Write-Host "⚠️  Tarea programada '$taskName' ya existe" -ForegroundColor Yellow
} else {
    try {
        $action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-File `"$(Join-Path (Get-Location) 'start_sabrositas_auto.ps1')`""
        $trigger = New-ScheduledTaskTrigger -AtStartup
        $principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
        
        Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description "Auto-deploy del Sistema POS Sabrositas"
        
        Write-Host "✅ Tarea programada '$taskName' creada para inicio automático" -ForegroundColor Green
    } catch {
        Write-Host "⚠️  No se pudo crear tarea programada: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Crear archivo de configuración
$config = @"
# ==============================================
# CONFIGURACIÓN DEL SISTEMA DE DESPLIEGUE AUTOMÁTICO
# Sistema POS Sabrositas v2.0.0 Enterprise
# ==============================================

# Configuración del monitor
MONITOR_INTERVAL_SECONDS=30
AUTO_DEPLOY_ON_STARTUP=true
SKIP_BACKUP_ON_AUTO_DEPLOY=false
VERBOSE_LOGGING=false

# Configuración de servicios
BACKEND_PORT=8000
FRONTEND_PORT=5173
HEALTH_CHECK_TIMEOUT=10

# Configuración de archivos a monitorear
WATCH_PATTERNS=app/**/*.py,frontend/src/**/*.tsx,frontend/src/**/*.ts,requirements.txt,frontend/package.json,config/**/*.py,*.py

# Configuración de logs
LOG_RETENTION_DAYS=30
MAX_LOG_SIZE_MB=100

# Configuración de backup
BACKUP_RETENTION_DAYS=7
AUTO_BACKUP_ON_DEPLOY=true
"@

$config | Out-File -FilePath "auto_deploy_config.env" -Encoding UTF8
Write-Host "✅ Archivo de configuración creado: auto_deploy_config.env" -ForegroundColor Green

Write-Host ""
Write-Host "🎯 SISTEMA DE DESPLIEGUE AUTOMÁTICO CONFIGURADO" -ForegroundColor Green
Write-Host "==============================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Archivos creados:" -ForegroundColor Cyan
Write-Host "   ✅ auto_deploy_system.ps1     - Sistema principal de despliegue" -ForegroundColor Green
Write-Host "   ✅ monitor_updates.ps1        - Monitor de actualizaciones" -ForegroundColor Green
Write-Host "   ✅ deploy_on_update.ps1       - Despliegue rápido en cambios" -ForegroundColor Green
Write-Host "   ✅ start_sabrositas_auto.ps1  - Script de inicio automático" -ForegroundColor Green
Write-Host "   ✅ auto_deploy_config.env     - Configuración del sistema" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 Comandos disponibles:" -ForegroundColor Cyan
Write-Host ""
Write-Host "   # Despliegue manual:" -ForegroundColor White
Write-Host "   .\auto_deploy_system.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "   # Despliegue forzado:" -ForegroundColor White
Write-Host "   .\auto_deploy_system.ps1 -ForceRestart" -ForegroundColor Yellow
Write-Host ""
Write-Host "   # Monitor de actualizaciones:" -ForegroundColor White
Write-Host "   .\monitor_updates.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "   # Monitor con intervalo personalizado:" -ForegroundColor White
Write-Host "   .\monitor_updates.ps1 -IntervalSeconds 60" -ForegroundColor Yellow
Write-Host ""
Write-Host "   # Despliegue rápido en cambios:" -ForegroundColor White
Write-Host "   .\deploy_on_update.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "   # Inicio automático completo:" -ForegroundColor White
Write-Host "   .\start_sabrositas_auto.ps1" -ForegroundColor Yellow
Write-Host ""
Write-Host "📊 El sistema ahora se desplegará automáticamente cuando:" -ForegroundColor Cyan
Write-Host "   • Se modifiquen archivos Python en app/" -ForegroundColor White
Write-Host "   • Se modifiquen archivos React en frontend/src/" -ForegroundColor White
Write-Host "   • Se actualice requirements.txt o package.json" -ForegroundColor White
Write-Host "   • Se detecten cambios en Git" -ForegroundColor White
Write-Host ""
Write-Host "🎉 ¡CONFIGURACIÓN COMPLETADA EXITOSAMENTE!" -ForegroundColor Green
Write-Host "===========================================" -ForegroundColor Green
