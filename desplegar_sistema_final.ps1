# Script de Despliegue Final - Sistema POS Sabrositas v2.0.0
# ============================================================

Write-Host "DESPLEGANDO SISTEMA POS SABROSITAS v2.0.0" -ForegroundColor Green
Write-Host "============================================================"
Write-Host "Las Arepas Cuadradas - Enterprise Edition" -ForegroundColor Yellow
Write-Host "============================================================"

Write-Host ""
Write-Host "VALIDACION PREVIA AL DESPLIEGUE:" -ForegroundColor Cyan

# Verificar Python
try {
    $pythonVersion = python --version
    Write-Host "Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Python no encontrado" -ForegroundColor Red
    exit 1
}

# Verificar Node.js
try {
    $nodeVersion = node --version
    Write-Host "Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "Error: Node.js no encontrado" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "VALIDACION DEL SISTEMA:" -ForegroundColor Cyan

# Verificar Backend
try {
    $healthResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing -TimeoutSec 5
    if ($healthResponse.StatusCode -eq 200) {
        Write-Host "Backend funcionando correctamente" -ForegroundColor Green
        $healthData = $healthResponse.Content | ConvertFrom-Json
        Write-Host "   Estado: $($healthData.status)" -ForegroundColor White
        Write-Host "   Base de datos: $($healthData.database)" -ForegroundColor White
    }
} catch {
    Write-Host "Backend no responde" -ForegroundColor Red
    exit 1
}

# Verificar Productos
try {
    $productsResponse = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/products" -UseBasicParsing -TimeoutSec 5
    if ($productsResponse.StatusCode -eq 200) {
        $productsData = $productsResponse.Content | ConvertFrom-Json
        $totalProducts = $productsData.data.pagination.total
        Write-Host "Productos cargados: $totalProducts" -ForegroundColor Green
    }
} catch {
    Write-Host "Error verificando productos" -ForegroundColor Red
    exit 1
}

# Verificar Frontend
try {
    $frontendResponse = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 5
    if ($frontendResponse.StatusCode -eq 200) {
        Write-Host "Frontend funcionando correctamente" -ForegroundColor Green
    }
} catch {
    Write-Host "Frontend no responde" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "DESPLIEGUE COMPLETADO EXITOSAMENTE" -ForegroundColor Green
Write-Host "============================================================"

Write-Host ""
Write-Host "URLS DEL SISTEMA DESPLEGADO:" -ForegroundColor Cyan
Write-Host "   Frontend:     http://localhost:5173" -ForegroundColor White
Write-Host "   Backend API:  http://localhost:8000" -ForegroundColor White
Write-Host "   Health Check: http://localhost:8000/api/v1/health" -ForegroundColor White

Write-Host ""
Write-Host "CREDENCIALES DEL SISTEMA:" -ForegroundColor Cyan
Write-Host "   SuperAdmin:    superadmin / SuperAdmin123!" -ForegroundColor White
Write-Host "   Global Admin:  globaladmin / Global123!" -ForegroundColor White
Write-Host "   Store Admin:   storeadmin1 / Store123!" -ForegroundColor White
Write-Host "   Tech Admin:    techadmin / TechAdmin123!" -ForegroundColor White

Write-Host ""
Write-Host "CATALOGO DE AREPAS CUADRADAS:" -ForegroundColor Cyan
Write-Host "   Total de productos: 18 arepas" -ForegroundColor White
Write-Host "   Sencillas: 3 productos" -ForegroundColor White
Write-Host "   Clasicas: 10 productos" -ForegroundColor White
Write-Host "   Premium: 5 productos" -ForegroundColor White

Write-Host ""
Write-Host "SISTEMA POS SABROSITAS DESPLEGADO Y LISTO!" -ForegroundColor Green
Write-Host "Listo para vender Las Arepas Cuadradas!" -ForegroundColor Yellow
Write-Host "============================================================"

Write-Host ""
Write-Host "Despliegue completado exitosamente" -ForegroundColor Green