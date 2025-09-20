@echo off
echo ========================================
echo    SISTEMA POS SABROSITAS v2.0.0
echo    Las Arepas Cuadradas - Enterprise
echo ========================================
echo.

echo [1/3] Iniciando Backend Flask...
start "Backend Sabrositas" cmd /k "cd /d C:\OdataSabrositas\Sistema_POS_Odata && python main.py"

echo [2/3] Esperando 10 segundos para que el backend se inicie...
timeout /t 10 /nobreak >nul

echo [3/3] Iniciando Frontend React...
start "Frontend Sabrositas" cmd /k "cd /d C:\OdataSabrositas\Sistema_POS_Odata\frontend && npm run dev"

echo.
echo ========================================
echo    SISTEMA INICIADO EXITOSAMENTE
echo ========================================
echo.
echo 🌐 URLs del Sistema:
echo    Frontend: http://localhost:5173
echo    Backend:  http://localhost:8000
echo    API:      http://localhost:8000/api/v1/health
echo.
echo 👥 Credenciales del Sistema:
echo    SuperAdmin:    superadmin / SuperAdmin123!
echo    Global Admin:  globaladmin / Global123!
echo    Store Admin:   storeadmin1 / Store123!
echo    Tech Admin:    techadmin / TechAdmin123!
echo.
echo Presiona cualquier tecla para abrir el navegador...
pause >nul

echo Abriendo navegador...
start http://localhost:5173

echo.
echo ¡Sistema Sabrositas listo para usar!
pause
