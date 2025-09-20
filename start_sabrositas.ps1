# Sistema POS Sabrositas v2.0.0 - Script de Inicio
# Las Arepas Cuadradas - Enterprise

Write-Host "========================================" -ForegroundColor Yellow
Write-Host "    SISTEMA POS SABROSITAS v2.0.0" -ForegroundColor Yellow
Write-Host "    Las Arepas Cuadradas - Enterprise" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""

# Función para verificar si un puerto está en uso
function Test-Port {
    param([int]$Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    }
    catch {
        return $false
    }
}

# Función para matar procesos en puertos específicos
function Stop-ProcessOnPort {
    param([int]$Port)
    $processes = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    foreach ($process in $processes) {
        Stop-Process -Id $process.OwningProcess -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "[1/4] Limpiando puertos..." -ForegroundColor Cyan
Stop-ProcessOnPort -Port 8000
Stop-ProcessOnPort -Port 5173
Start-Sleep -Seconds 2

Write-Host "[2/4] Iniciando Backend Flask..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    Set-Location "C:\OdataSabrositas\Sistema_POS_Odata"
    python main.py
}

Write-Host "[3/4] Esperando que el backend se inicie..." -ForegroundColor Yellow
$timeout = 30
$elapsed = 0
do {
    Start-Sleep -Seconds 1
    $elapsed++
    if (Test-Port -Port 8000) {
        Write-Host "✅ Backend iniciado correctamente" -ForegroundColor Green
        break
    }
    if ($elapsed -ge $timeout) {
        Write-Host "❌ Timeout esperando el backend" -ForegroundColor Red
        exit 1
    }
} while ($true)

Write-Host "[4/4] Iniciando Frontend React..." -ForegroundColor Blue
$frontendJob = Start-Job -ScriptBlock {
    Set-Location "C:\OdataSabrositas\Sistema_POS_Odata\frontend"
    npm run dev
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Yellow
Write-Host "    SISTEMA INICIADO EXITOSAMENTE" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Yellow
Write-Host ""
Write-Host "🌐 URLs del Sistema:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "   Backend:  http://localhost:8000" -ForegroundColor White
Write-Host "   API:      http://localhost:8000/api/v1/health" -ForegroundColor White
Write-Host ""
Write-Host "👥 Credenciales del Sistema:" -ForegroundColor Cyan
Write-Host "   SuperAdmin:    superadmin / SuperAdmin123!" -ForegroundColor White
Write-Host "   Global Admin:  globaladmin / Global123!" -ForegroundColor White
Write-Host "   Store Admin:   storeadmin1 / Store123!" -ForegroundColor White
Write-Host "   Tech Admin:    techadmin / TechAdmin123!" -ForegroundColor White
Write-Host ""

# Esperar a que el frontend se inicie
Write-Host "Esperando que el frontend se inicie..." -ForegroundColor Yellow
$timeout = 30
$elapsed = 0
do {
    Start-Sleep -Seconds 1
    $elapsed++
    if (Test-Port -Port 5173) {
        Write-Host "✅ Frontend iniciado correctamente" -ForegroundColor Green
        break
    }
    if ($elapsed -ge $timeout) {
        Write-Host "⚠️ Frontend tardando en iniciar, pero el sistema está funcionando" -ForegroundColor Yellow
        break
    }
} while ($true)

Write-Host ""
Write-Host "🚀 Abriendo navegador..." -ForegroundColor Green
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "¡Sistema Sabrositas listo para usar!" -ForegroundColor Green
Write-Host "Presiona Ctrl+C para detener los servicios" -ForegroundColor Yellow

# Mantener el script ejecutándose
try {
    while ($true) {
        Start-Sleep -Seconds 10
        if (-not (Test-Port -Port 8000)) {
            Write-Host "❌ Backend desconectado" -ForegroundColor Red
            break
        }
    }
}
finally {
    Write-Host "Deteniendo servicios..." -ForegroundColor Yellow
    Stop-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
}
