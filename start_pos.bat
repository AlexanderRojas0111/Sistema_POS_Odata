@echo off
chcp 65001 >nul
title Sistema POS O'data v2.0.0

echo.
echo ========================================
echo    🚀 SISTEMA POS O'DATA v2.0.0
echo ========================================
echo.
echo 🎯 Iniciando despliegue completo...
echo.

REM Verificar si el entorno virtual existe
if not exist "venv_pos_clean\Scripts\activate.bat" (
    echo ❌ Entorno virtual no encontrado
    echo 💡 Ejecuta: python -m venv venv_pos_clean
    echo 💡 Luego: venv_pos_clean\Scripts\activate.bat
    pause
    exit /b 1
)

REM Activar entorno virtual
echo 🔧 Activando entorno virtual...
call venv_pos_clean\Scripts\activate.bat

REM Verificar dependencias
echo.
echo 🔍 Verificando dependencias...
python -c "import flask, sklearn, waitress" 2>nul
if errorlevel 1 (
    echo ❌ Faltan dependencias
    echo 💡 Instalando dependencias...
    pip install -r requirements.txt
)

REM Ejecutar script de despliegue
echo.
echo 🚀 Ejecutando despliegue completo...
python deploy_windows.py

echo.
echo ✅ Proceso completado
pause
