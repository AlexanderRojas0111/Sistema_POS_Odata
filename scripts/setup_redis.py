#!/usr/bin/env python3
"""
Script de Configuración de Redis - O'Data v2.0.0
================================================

Este script configura Redis para:
- Instalación en Windows
- Configuración de seguridad
- Optimización de rendimiento
- Configuración de persistencia

Autor: Sistema POS Odata
Versión: 2.0.0
"""

import os
import sys
import subprocess
import json
import logging
import argparse
from pathlib import Path
import urllib.request
import zipfile
import shutil

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('redis_setup.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RedisSetup:
    """Configurador de Redis para Windows"""
    
    def __init__(self, install_dir: str = None):
        self.install_dir = install_dir or "C:\\Redis"
        self.redis_version = "5.0.14.1"
        self.redis_url = f"https://github.com/microsoftarchive/redis/releases/download/win-{self.redis_version}/Redis-x64-{self.redis_version}.msi"
        self.redis_exe = "redis-server.exe"
        self.redis_cli = "redis-cli.exe"
        
    def check_windows(self) -> bool:
        """Verificar que estamos en Windows"""
        if os.name != 'nt':
            logger.error("Este script solo funciona en Windows")
            return False
        return True
    
    def check_admin_privileges(self) -> bool:
        """Verificar privilegios de administrador"""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
    
    def download_redis(self) -> bool:
        """Descargar Redis para Windows"""
        try:
            logger.info(f"Descargando Redis {self.redis_version}...")
            
            # Crear directorio temporal
            temp_dir = Path("temp_redis")
            temp_dir.mkdir(exist_ok=True)
            
            # Descargar archivo
            msi_path = temp_dir / f"Redis-x64-{self.redis_version}.msi"
            
            with urllib.request.urlopen(self.redis_url) as response:
                with open(msi_path, 'wb') as f:
                    shutil.copyfileobj(response, f)
            
            logger.info(f"Redis descargado en: {msi_path}")
            return str(msi_path)
            
        except Exception as e:
            logger.error(f"Error descargando Redis: {e}")
            return None
    
    def install_redis_msi(self, msi_path: str) -> bool:
        """Instalar Redis usando MSI"""
        try:
            logger.info("Instalando Redis...")
            
            # Comando de instalación silenciosa
            cmd = [
                'msiexec',
                '/i', msi_path,
                '/quiet',
                '/norestart',
                f'TARGETDIR={self.install_dir}',
                'ADDLOCAL=ALL'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Redis instalado exitosamente")
                return True
            else:
                logger.error(f"Error en instalación: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error instalando Redis: {e}")
            return False
    
    def create_redis_config(self) -> bool:
        """Crear archivo de configuración de Redis"""
        try:
            config_dir = Path(self.install_dir) / "config"
            config_dir.mkdir(exist_ok=True)
            
            config_file = config_dir / "redis.conf"
            
            # Configuración optimizada para producción
            config_content = f"""# Configuración de Redis para O'Data POS v2.0.0
# Archivo: {config_file}
# Generado automáticamente

# Configuración de red
bind 127.0.0.1
port 6379
tcp-backlog 511
timeout 0
tcp-keepalive 300

# Configuración general
daemonize no
supervised no
pidfile {self.install_dir}\\redis.pid
loglevel notice
logfile {self.install_dir}\\redis.log
databases 16

# Configuración de snapshots
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir {self.install_dir}

# Configuración de replicación
replica-serve-stale-data yes
replica-read-only yes
repl-diskless-sync no
repl-diskless-sync-delay 5
repl-ping-replica-period 10
repl-timeout 60
repl-disable-tcp-nodelay no

# Configuración de seguridad
requirepass odata_redis_password_2024
maxclients 10000

# Configuración de memoria
maxmemory 256mb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# Configuración de AOF
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Configuración de Lua
lua-time-limit 5000

# Configuración de slow log
slowlog-log-slower-than 10000
slowlog-max-len 128

# Configuración de latencia
latency-monitor-threshold 0

# Configuración de notificaciones
notify-keyspace-events ""

# Configuración de hash
hash-max-ziplist-entries 512
hash-max-ziplist-value 64

# Configuración de list
list-max-ziplist-size -2

# Configuración de set
set-max-intset-entries 512

# Configuración de zset
zset-max-ziplist-entries 128
zset-max-ziplist-value 64

# Configuración de hll
hll-sparse-max-bytes 3000

# Configuración de activerehashing
activerehashing yes

# Configuración de client-output-buffer-limit
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit replica 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60

# Configuración de hz
hz 10

# Configuración de aof-rewrite-incremental-fsync
aof-rewrite-incremental-fsync yes
"""
            
            with open(config_file, 'w') as f:
                f.write(config_content)
            
            logger.info(f"Archivo de configuración creado: {config_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando configuración: {e}")
            return False
    
    def create_windows_service(self) -> bool:
        """Crear servicio de Windows para Redis"""
        try:
            logger.info("Creando servicio de Windows para Redis...")
            
            # Ruta al ejecutable de Redis
            redis_exe_path = Path(self.install_dir) / self.redis_exe
            config_path = Path(self.install_dir) / "config" / "redis.conf"
            
            if not redis_exe_path.exists():
                logger.error(f"Ejecutable de Redis no encontrado: {redis_exe_path}")
                return False
            
            # Crear servicio usando sc.exe
            service_name = "Redis"
            service_display_name = "Redis Server for O'Data POS"
            
            cmd = [
                'sc', 'create', service_name,
                'binPath=', f'"{redis_exe_path}" "{config_path}"',
                'DisplayName=', service_display_name,
                'start=', 'auto'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Servicio de Redis creado exitosamente")
                
                # Configurar descripción del servicio
                desc_cmd = [
                    'sc', 'description', service_name,
                    'Redis in-memory data structure store for O\'Data POS v2.0.0'
                ]
                subprocess.run(desc_cmd, capture_output=True)
                
                return True
            else:
                logger.error(f"Error creando servicio: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error creando servicio: {e}")
            return False
    
    def start_redis_service(self) -> bool:
        """Iniciar servicio de Redis"""
        try:
            logger.info("Iniciando servicio de Redis...")
            
            cmd = ['sc', 'start', 'Redis']
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("Servicio de Redis iniciado")
                return True
            else:
                logger.error(f"Error iniciando servicio: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error iniciando servicio: {e}")
            return False
    
    def test_redis_connection(self) -> bool:
        """Probar conexión a Redis"""
        try:
            logger.info("Probando conexión a Redis...")
            
            # Esperar un momento para que Redis se inicie
            import time
            time.sleep(3)
            
            # Probar conexión usando redis-cli
            redis_cli_path = Path(self.install_dir) / self.redis_cli
            
            if not redis_cli_path.exists():
                logger.error(f"Redis CLI no encontrado: {redis_cli_path}")
                return False
            
            # Probar ping
            cmd = [str(redis_cli_path), '-a', 'odata_redis_password_2024', 'ping']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and 'PONG' in result.stdout:
                logger.info("Conexión a Redis exitosa ✓")
                return True
            else:
                logger.error(f"Error en conexión: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error probando conexión: {e}")
            return False
    
    def create_environment_script(self) -> bool:
        """Crear script para configurar variables de entorno"""
        try:
            script_content = f"""@echo off
REM Script para configurar variables de entorno de Redis
REM Archivo: setup_redis_env.bat

echo Configurando variables de entorno para Redis...

REM Agregar Redis al PATH
setx PATH "%PATH%;{self.install_dir}" /M

REM Configurar variables de entorno para O'Data POS
setx REDIS_HOST "127.0.0.1" /M
setx REDIS_PORT "6379" /M
setx REDIS_PASSWORD "odata_redis_password_2024" /M
setx REDIS_USE_CACHE "True" /M
setx REDIS_USE_RATE_LIMIT "True" /M

echo Variables de entorno configuradas.
echo Reinicia la consola para aplicar los cambios.
pause
"""
            
            script_path = Path("setup_redis_env.bat")
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            logger.info(f"Script de configuración creado: {script_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando script: {e}")
            return False
    
    def create_redis_manager_script(self) -> bool:
        """Crear script para gestionar Redis"""
        try:
            script_content = f"""@echo off
REM Script para gestionar Redis - O'Data POS v2.0.0
REM Archivo: manage_redis.bat

:menu
cls
echo ========================================
echo    GESTOR DE REDIS - O'Data POS v2.0.0
echo ========================================
echo.
echo 1. Iniciar Redis
echo 2. Detener Redis
echo 3. Reiniciar Redis
echo 4. Estado del servicio
echo 5. Ver logs
echo 6. Probar conexión
echo 7. Salir
echo.
set /p choice="Selecciona una opción (1-7): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto status
if "%choice%"=="5" goto logs
if "%choice%"=="6" goto test
if "%choice%"=="7" goto exit
goto menu

:start
echo.
echo Iniciando Redis...
sc start Redis
if %errorlevel%==0 (
    echo Redis iniciado exitosamente.
) else (
    echo Error iniciando Redis.
)
pause
goto menu

:stop
echo.
echo Deteniendo Redis...
sc stop Redis
if %errorlevel%==0 (
    echo Redis detenido exitosamente.
) else (
    echo Error deteniendo Redis.
)
pause
goto menu

:restart
echo.
echo Reiniciando Redis...
sc stop Redis
timeout /t 3 /nobreak >nul
sc start Redis
if %errorlevel%==0 (
    echo Redis reiniciado exitosamente.
) else (
    echo Error reiniciando Redis.
)
pause
goto menu

:status
echo.
echo Estado del servicio Redis:
sc query Redis
pause
goto menu

:logs
echo.
echo Mostrando logs de Redis:
if exist "{self.install_dir}\\redis.log" (
    type "{self.install_dir}\\redis.log"
) else (
    echo Archivo de log no encontrado.
)
pause
goto menu

:test
echo.
echo Probando conexión a Redis...
"{self.install_dir}\\redis-cli.exe" -a odata_redis_password_2024 ping
pause
goto menu

:exit
echo.
echo ¡Hasta luego!
exit /b 0
"""
            
            script_path = Path("manage_redis.bat")
            with open(script_path, 'w') as f:
                f.write(script_content)
            
            logger.info(f"Script de gestión creado: {script_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creando script de gestión: {e}")
            return False
    
    def setup(self) -> bool:
        """Ejecutar configuración completa de Redis"""
        try:
            logger.info("=== CONFIGURACIÓN DE REDIS PARA O'DATA POS v2.0.0 ===")
            
            # Verificar requisitos
            if not self.check_windows():
                return False
            
            if not self.check_admin_privileges():
                logger.error("Este script requiere privilegios de administrador")
                return False
            
            # Crear directorio de instalación
            Path(self.install_dir).mkdir(parents=True, exist_ok=True)
            
            # Descargar e instalar Redis
            msi_path = self.download_redis()
            if not msi_path:
                return False
            
            if not self.install_redis_msi(msi_path):
                return False
            
            # Crear configuración
            if not self.create_redis_config():
                return False
            
            # Crear servicio de Windows
            if not self.create_windows_service():
                return False
            
            # Iniciar servicio
            if not self.start_redis_service():
                return False
            
            # Probar conexión
            if not self.test_redis_connection():
                return False
            
            # Crear scripts de utilidad
            self.create_environment_script()
            self.create_redis_manager_script()
            
            # Limpiar archivos temporales
            try:
                shutil.rmtree("temp_redis")
            except:
                pass
            
            logger.info("=== CONFIGURACIÓN DE REDIS COMPLETADA ===")
            logger.info(f"Redis instalado en: {self.install_dir}")
            logger.info("Contraseña: odata_redis_password_2024")
            logger.info("Puerto: 6379")
            logger.info("Scripts creados: setup_redis_env.bat, manage_redis.bat")
            
            return True
            
        except Exception as e:
            logger.error(f"Error en configuración: {e}")
            return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Configurar Redis para O\'Data POS')
    parser.add_argument('--install-dir', default='C:\\Redis', help='Directorio de instalación')
    parser.add_argument('--dry-run', action='store_true', help='Solo mostrar qué se haría')
    
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("=== DRY RUN - No se realizarán cambios ===")
        logger.info(f"Directorio de instalación: {args.install_dir}")
        logger.info("Se instalaría Redis con configuración optimizada")
        return
    
    # Crear configurador y ejecutar
    setup = RedisSetup(args.install_dir)
    
    if setup.setup():
        logger.info("Configuración de Redis exitosa!")
        sys.exit(0)
    else:
        logger.error("Configuración de Redis falló!")
        sys.exit(1)

if __name__ == '__main__':
    main()
