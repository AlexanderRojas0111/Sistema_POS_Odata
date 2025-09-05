@echo off
REM ========================================================================
REM Sistema POS O'data - Activación del Entorno Virtual
REM ========================================================================
REM Versión: 2.0.0
REM Descripción: Script para activar el entorno virtual de Python 3.13
REM ========================================================================

echo.
echo 🚀 Sistema POS O'Data v2.0.0 - Activación del Entorno Virtual
echo ========================================================================
echo.

REM Verificar si el entorno virtual existe
if not exist "venv_python313\Scripts\activate.bat" (
    echo ❌ Error: El entorno virtual 'venv_python313' no existe.
    echo.
    echo Para crear el entorno virtual, ejecuta:
    echo   py -3.13 -m venv venv_python313
    echo.
    pause
    exit /b 1
)

REM Activar el entorno virtual
echo ✅ Activando entorno virtual de Python 3.13...
call venv_python313\Scripts\activate.bat

REM Verificar la versión de Python
echo.
echo 📍 Verificando versión de Python...
python --version

echo.
echo ✅ Entorno virtual activado correctamente!
echo.
echo 📋 Comandos disponibles:
echo   python --version                    # Ver versión de Python
echo   pip list                           # Listar paquetes instalados
echo   pytest --version                   # Ver versión de pytest
echo   black --version                    # Ver versión de black
echo   flake8 --version                   # Ver versión de flake8
echo.
echo 🚀 Para ejecutar la suite de validación:
echo   python run_validation_suite.py
echo.
echo 🧹 Para desactivar el entorno virtual:
echo   deactivate
echo.

REM Mantener la consola abierta
cmd /k
