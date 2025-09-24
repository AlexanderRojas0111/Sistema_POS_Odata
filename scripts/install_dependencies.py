#!/usr/bin/env python3
"""
Script de instalación automática de dependencias para Sistema POS Odata
Instala todas las dependencias necesarias según el entorno especificado
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path
from typing import List, Optional
import platform

# Configuración de entornos
ENVIRONMENTS = {
    'dev': 'requirements.dev.txt',
    'development': 'requirements.dev.txt',
    'staging': 'requirements.staging.txt',
    'prod': 'requirements.production.txt',
    'production': 'requirements.production.txt',
    'minimal': 'requirements.minimal.txt',
    'lock': 'requirements.lock'
}

# Comandos de instalación según el sistema operativo
INSTALL_COMMANDS = {
    'Windows': {
        'pip': 'python -m pip',
        'upgrade': 'python -m pip install --upgrade pip',
        'install': 'python -m pip install -r'
    },
    'Linux': {
        'pip': 'pip3',
        'upgrade': 'pip3 install --upgrade pip',
        'install': 'pip3 install -r'
    },
    'Darwin': {  # macOS
        'pip': 'pip3',
        'upgrade': 'pip3 install --upgrade pip',
        'install': 'pip3 install -r'
    }
}

def get_system_info() -> dict:
    """Obtiene información del sistema operativo"""
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'python_version': platform.python_version()
    }

def get_install_commands() -> dict:
    """Obtiene los comandos de instalación para el sistema actual"""
    system = platform.system()
    return INSTALL_COMMANDS.get(system, INSTALL_COMMANDS['Linux'])

def check_python_version() -> bool:
    """Verifica que la versión de Python sea compatible"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 13:
        return True
    return False

def run_command(command: str, description: str = "") -> bool:
    """Ejecuta un comando del sistema"""
    try:
        if description:
            print(f"🔄 {description}...")
        
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        
        if description:
            print(f"✅ {description} completado")
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando: {command}")
        print(f"   Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

def upgrade_pip() -> bool:
    """Actualiza pip a la última versión"""
    commands = get_install_commands()
    return run_command(commands['upgrade'], "Actualizando pip")

def install_requirements_file(requirements_file: str, upgrade: bool = False) -> bool:
    """Instala las dependencias de un archivo de requirements"""
    if not Path(requirements_file).exists():
        print(f"❌ Archivo no encontrado: {requirements_file}")
        return False
    
    commands = get_install_commands()
    install_cmd = f"{commands['install']} {requirements_file}"
    
    if upgrade:
        install_cmd += " --upgrade"
    
    return run_command(install_cmd, f"Instalando dependencias desde {requirements_file}")

def install_package(package: str, upgrade: bool = False) -> bool:
    """Instala un paquete específico"""
    commands = get_install_commands()
    install_cmd = f"{commands['pip']} install {package}"
    
    if upgrade:
        install_cmd += " --upgrade"
    
    return run_command(install_cmd, f"Instalando {package}")

def install_core_dependencies() -> bool:
    """Instala dependencias core básicas"""
    core_packages = [
        'setuptools',
        'wheel',
        'packaging'
    ]
    
    success = True
    for package in core_packages:
        if not install_package(package):
            success = False
    
    return success

def validate_installation(requirements_file: str) -> bool:
    """Valida que la instalación fue exitosa"""
    try:
        # Intentar importar algunas librerías clave
        import importlib
        
        # Lista de librerías críticas para verificar
        critical_libs = ['flask', 'sqlalchemy', 'psycopg2', 'redis', 'celery']
        
        for lib in critical_libs:
            try:
                importlib.import_module(lib)
                print(f"✅ {lib} importado correctamente")
            except ImportError:
                print(f"❌ {lib} no se pudo importar")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error durante la validación: {e}")
        return False

def create_virtual_environment(env_name: str = "pos_odata_env") -> bool:
    """Crea un entorno virtual"""
    try:
        print(f"🔄 Creando entorno virtual: {env_name}")
        
        # Crear entorno virtual
        if not run_command(f"python -m venv {env_name}", f"Creando entorno virtual {env_name}"):
            return False
        
        # Activar entorno virtual (Windows)
        if platform.system() == "Windows":
            activate_script = f"{env_name}\\Scripts\\activate"
            print(f"📝 Para activar el entorno virtual, ejecuta: {activate_script}")
        else:
            activate_script = f"source {env_name}/bin/activate"
            print(f"📝 Para activar el entorno virtual, ejecuta: {activate_script}")
        
        return True
    except Exception as e:
        print(f"❌ Error creando entorno virtual: {e}")
        return False

def print_system_info():
    """Imprime información del sistema"""
    info = get_system_info()
    print("=" * 60)
    print("INFORMACIÓN DEL SISTEMA")
    print("=" * 60)
    print(f"Sistema Operativo: {info['system']} {info['release']}")
    print(f"Arquitectura: {info['machine']}")
    print(f"Versión de Python: {info['python_version']}")
    print("=" * 60)
    print()

def print_usage():
    """Imprime información de uso"""
    print("USO:")
    print("  python install_dependencies.py [ENTORNO] [OPCIONES]")
    print()
    print("ENTORNOS DISPONIBLES:")
    for env, file in ENVIRONMENTS.items():
        print(f"  {env:12} -> {file}")
    print()
    print("OPCIONES:")
    print("  --upgrade        Actualiza paquetes existentes")
    print("  --create-env     Crea un entorno virtual")
    print("  --validate       Valida la instalación")
    print("  --help           Muestra esta ayuda")
    print()
    print("EJEMPLOS:")
    print("  python install_dependencies.py dev")
    print("  python install_dependencies.py production --upgrade")
    print("  python install_dependencies.py minimal --create-env")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Instalador de dependencias para Sistema POS Odata",
        add_help=False
    )
    
    parser.add_argument('environment', nargs='?', default='dev',
                       help='Entorno a instalar (dev, staging, production, minimal)')
    parser.add_argument('--upgrade', action='store_true',
                       help='Actualiza paquetes existentes')
    parser.add_argument('--create-env', action='store_true',
                       help='Crea un entorno virtual')
    parser.add_argument('--validate', action='store_true',
                       help='Valida la instalación')
    parser.add_argument('--help', action='store_true',
                       help='Muestra la ayuda')
    
    args = parser.parse_args()
    
    if args.help:
        print_usage()
        return
    
    # Verificar versión de Python
    if not check_python_version():
        print("❌ Se requiere Python 3.13 o superior")
        print(f"   Versión actual: {sys.version}")
        sys.exit(1)
    
    # Mostrar información del sistema
    print_system_info()
    
    # Obtener archivo de requirements
    env = args.environment.lower()
    if env not in ENVIRONMENTS:
        print(f"❌ Entorno no válido: {env}")
        print("   Entornos disponibles:", ", ".join(ENVIRONMENTS.keys()))
        sys.exit(1)
    
    requirements_file = ENVIRONMENTS[env]
    print(f"🎯 Instalando dependencias para entorno: {env}")
    print(f"📁 Archivo de requirements: {requirements_file}")
    print()
    
    # Crear entorno virtual si se solicita
    if args.create_env:
        if not create_virtual_environment():
            sys.exit(1)
        print()
    
    # Actualizar pip
    if not upgrade_pip():
        print("⚠️  No se pudo actualizar pip, continuando...")
    print()
    
    # Instalar dependencias core
    if not install_core_dependencies():
        print("⚠️  No se pudieron instalar todas las dependencias core")
    print()
    
    # Instalar dependencias del archivo de requirements
    if not install_requirements_file(requirements_file, args.upgrade):
        print(f"❌ Error instalando dependencias desde {requirements_file}")
        sys.exit(1)
    
    print()
    
    # Validar instalación si se solicita
    if args.validate:
        print("🔍 Validando instalación...")
        if validate_installation(requirements_file):
            print("✅ Instalación validada correctamente")
        else:
            print("❌ La instalación no se pudo validar")
            sys.exit(1)
    
    print("🎉 Instalación completada exitosamente!")
    print(f"📦 Entorno: {env}")
    print(f"📁 Requirements: {requirements_file}")
    
    if args.create_env:
        print("📝 Recuerda activar el entorno virtual antes de usar el sistema")

if __name__ == "__main__":
    main()
