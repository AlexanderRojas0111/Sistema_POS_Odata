#!/usr/bin/env python3
"""
Script de despliegue completo del Sistema POS Odata
Incluye validación, instalación de dependencias y configuración del sistema
"""

import sys
import subprocess
import argparse
import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import platform
import time

# Configuración del sistema
SYSTEM_CONFIG = {
    'name': 'Sistema POS Odata',
    'version': '2.0.0',
    'python_min_version': '3.13.0',
    'required_services': ['postgresql', 'redis', 'nginx'],
    'supported_platforms': ['Windows', 'Linux', 'Darwin']
}

# Pasos del despliegue
DEPLOYMENT_STEPS = [
    'validate_system',
    'check_dependencies',
    'install_dependencies',
    'setup_database',
    'setup_redis',
    'configure_environment',
    'test_system',
    'start_services'
]

def print_banner():
    """Imprime el banner del sistema"""
    print("=" * 80)
    print("🚀 SISTEMA POS ODATA - DESPLIEGUE AUTOMÁTICO")
    print("=" * 80)
    print(f"📦 Sistema: {SYSTEM_CONFIG['name']}")
    print(f"🔢 Versión: {SYSTEM_CONFIG['version']}")
    print(f"🐍 Python: {SYSTEM_CONFIG['python_min_version']}+")
    print(f"💻 Plataforma: {platform.system()}")
    print("=" * 80)
    print()

def check_system_requirements() -> Dict[str, bool]:
    """Verifica los requisitos del sistema"""
    print("🔍 Verificando requisitos del sistema...")
    
    checks = {}
    
    # Verificar Python
    python_version = sys.version_info
    checks['python'] = python_version.major == 3 and python_version.minor >= 13
    
    # Verificar sistema operativo
    checks['platform'] = platform.system() in SYSTEM_CONFIG['supported_platforms']
    
    # Verificar permisos de escritura
    checks['permissions'] = os.access('.', os.W_OK)
    
    # Verificar espacio en disco
    try:
        import shutil
        total, used, free = shutil.disk_usage('.')
        checks['disk_space'] = free > 1024 * 1024 * 1024 * 10  # 10GB mínimo
    except:
        checks['disk_space'] = True  # No se pudo verificar
    
    # Verificar conectividad de red
    try:
        import urllib.request
        urllib.request.urlopen('http://www.google.com', timeout=5)
        checks['network'] = True
    except:
        checks['network'] = False
    
    return checks

def print_system_checks(checks: Dict[str, bool]):
    """Imprime el resultado de las verificaciones del sistema"""
    print("📋 RESULTADO DE VERIFICACIONES:")
    for check, status in checks.items():
        icon = "✅" if status else "❌"
        print(f"   {icon} {check}")
    print()
    
    all_passed = all(checks.values())
    if all_passed:
        print("✅ Todos los requisitos del sistema están cumplidos")
    else:
        print("❌ Algunos requisitos del sistema no están cumplidos")
    
    return all_passed

def run_command_with_output(command: str, description: str = "") -> tuple:
    """Ejecuta un comando y retorna el resultado"""
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
        
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando: {command}")
        print(f"   Error: {e.stderr}")
        return False, e.stderr
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False, str(e)

def validate_dependencies() -> bool:
    """Valida las dependencias del sistema"""
    print("🔍 Validando dependencias...")
    
    # Ejecutar script de validación
    validation_script = Path("scripts/validate_dependencies.py")
    if validation_script.exists():
        success, output = run_command_with_output(
            f"python {validation_script}",
            "Ejecutando validación de dependencias"
        )
        return success
    else:
        print("⚠️  Script de validación no encontrado, saltando...")
        return True

def install_dependencies(environment: str = 'production') -> bool:
    """Instala las dependencias del sistema"""
    print(f"📦 Instalando dependencias para entorno: {environment}")
    
    # Ejecutar script de instalación
    install_script = Path("scripts/install_dependencies.py")
    if install_script.exists():
        success, output = run_command_with_output(
            f"python {install_script} {environment} --validate",
            f"Instalando dependencias para {environment}"
        )
        return success
    else:
        print("⚠️  Script de instalación no encontrado, saltando...")
        return True

def setup_database() -> bool:
    """Configura la base de datos"""
    print("🗄️  Configurando base de datos...")
    
    # Verificar si Docker está disponible
    docker_available, _ = run_command_with_output("docker --version", "Verificando Docker")
    
    if docker_available:
        # Usar Docker Compose
        if Path("docker-compose.yml").exists():
            success, output = run_command_with_output(
                "docker-compose up -d db",
                "Iniciando base de datos con Docker"
            )
            return success
        else:
            print("⚠️  docker-compose.yml no encontrado")
            return False
    else:
        print("⚠️  Docker no está disponible, configurar base de datos manualmente")
        return False

def setup_redis() -> bool:
    """Configura Redis"""
    print("🔴 Configurando Redis...")
    
    # Verificar si Docker está disponible
    docker_available, _ = run_command_with_output("docker --version", "Verificando Docker")
    
    if docker_available:
        # Usar Docker Compose
        if Path("docker-compose.yml").exists():
            success, output = run_command_with_output(
                "docker-compose up -d redis",
                "Iniciando Redis con Docker"
            )
            return success
        else:
            print("⚠️  docker-compose.yml no encontrado")
            return False
    else:
        print("⚠️  Docker no está disponible, configurar Redis manualmente")
        return False

def configure_environment() -> bool:
    """Configura las variables de entorno"""
    print("⚙️  Configurando variables de entorno...")
    
    # Verificar archivos de entorno
    env_files = ['env.production', 'env.staging', 'env.development']
    env_file = None
    
    for file in env_files:
        if Path(file).exists():
            env_file = file
            break
    
    if env_file:
        print(f"📁 Archivo de entorno encontrado: {env_file}")
        
        # Crear .env si no existe
        if not Path('.env').exists():
            try:
                import shutil
                shutil.copy(env_file, '.env')
                print("✅ Archivo .env creado")
                return True
            except Exception as e:
                print(f"❌ Error creando .env: {e}")
                return False
        else:
            print("✅ Archivo .env ya existe")
            return True
    else:
        print("⚠️  No se encontraron archivos de entorno")
        return False

def test_system() -> bool:
    """Prueba el sistema"""
    print("🧪 Probando el sistema...")
    
    # Verificar que la aplicación se puede importar
    try:
        import app.main
        print("✅ Aplicación principal importada correctamente")
    except ImportError as e:
        print(f"❌ Error importando aplicación: {e}")
        return False
    
    # Verificar endpoints básicos
    try:
        from app.main import app
        with app.test_client() as client:
            response = client.get('/health')
            if response.status_code == 200:
                print("✅ Endpoint de salud funcionando")
            else:
                print(f"⚠️  Endpoint de salud retornó código: {response.status_code}")
    except Exception as e:
        print(f"⚠️  No se pudo probar endpoint de salud: {e}")
    
    return True

def start_services() -> bool:
    """Inicia los servicios del sistema"""
    print("🚀 Iniciando servicios...")
    
    # Verificar si Docker está disponible
    docker_available, _ = run_command_with_output("docker --version", "Verificando Docker")
    
    if docker_available:
        # Usar Docker Compose
        if Path("docker-compose.yml").exists():
            success, output = run_command_with_output(
                "docker-compose up -d",
                "Iniciando todos los servicios con Docker"
            )
            return success
        else:
            print("⚠️  docker-compose.yml no encontrado")
            return False
    else:
        print("⚠️  Docker no está disponible, iniciar servicios manualmente")
        return False

def generate_deployment_report(steps_results: Dict[str, bool]) -> Dict:
    """Genera un reporte del despliegue"""
    total_steps = len(steps_results)
    successful_steps = sum(1 for result in steps_results.values() if result)
    failed_steps = total_steps - successful_steps
    
    report = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'system': SYSTEM_CONFIG['name'],
        'version': SYSTEM_CONFIG['version'],
        'platform': platform.system(),
        'python_version': sys.version,
        'deployment_summary': {
            'total_steps': total_steps,
            'successful': successful_steps,
            'failed': failed_steps,
            'success_rate': (successful_steps / total_steps) * 100 if total_steps > 0 else 0
        },
        'step_results': steps_results,
        'overall_success': failed_steps == 0
    }
    
    return report

def print_deployment_report(report: Dict):
    """Imprime el reporte del despliegue"""
    print("=" * 80)
    print("📊 REPORTE DE DESPLIEGUE")
    print("=" * 80)
    print(f"📅 Fecha: {report['timestamp']}")
    print(f"💻 Sistema: {report['system']} v{report['version']}")
    print(f"🖥️  Plataforma: {report['platform']}")
    print(f"🐍 Python: {report['python_version']}")
    print()
    
    summary = report['deployment_summary']
    print(f"📈 RESUMEN:")
    print(f"   Total de pasos: {summary['total_steps']}")
    print(f"   Exitosos: {summary['successful']}")
    print(f"   Fallidos: {summary['failed']}")
    print(f"   Tasa de éxito: {summary['success_rate']:.1f}%")
    print()
    
    print("📋 DETALLE DE PASOS:")
    for step, result in report['step_results'].items():
        icon = "✅" if result else "❌"
        print(f"   {icon} {step}")
    print()
    
    if report['overall_success']:
        print("🎉 ¡DESPLIEGUE COMPLETADO EXITOSAMENTE!")
        print("   El sistema está listo para usar")
    else:
        print("❌ DESPLIEGUE INCOMPLETO")
        print("   Revisar los pasos fallidos e intentar nuevamente")
    
    print("=" * 80)

def save_deployment_report(report: Dict, filename: str = "deployment_report.json"):
    """Guarda el reporte del despliegue"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"📄 Reporte guardado en: {filename}")
    except Exception as e:
        print(f"❌ Error al guardar reporte: {e}")

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Despliegue automático del Sistema POS Odata"
    )
    
    parser.add_argument('--environment', '-e', default='production',
                       choices=['development', 'staging', 'production'],
                       help='Entorno de despliegue')
    parser.add_argument('--skip-validation', action='store_true',
                       help='Saltar validación de dependencias')
    parser.add_argument('--skip-install', action='store_true',
                       help='Saltar instalación de dependencias')
    parser.add_argument('--dry-run', action='store_true',
                       help='Simular despliegue sin ejecutar cambios')
    
    args = parser.parse_args()
    
    # Mostrar banner
    print_banner()
    
    # Verificar requisitos del sistema
    system_checks = check_system_requirements()
    if not print_system_checks(system_checks):
        print("❌ No se pueden cumplir los requisitos del sistema")
        sys.exit(1)
    
    # Ejecutar pasos del despliegue
    steps_results = {}
    
    for step in DEPLOYMENT_STEPS:
        print(f"\n{'='*60}")
        print(f"PASO: {step.upper()}")
        print(f"{'='*60}")
        
        if args.dry_run:
            print(f"🔍 [DRY RUN] Simulando: {step}")
            steps_results[step] = True
            continue
        
        # Ejecutar paso según su nombre
        if step == 'validate_system':
            steps_results[step] = True  # Ya se hizo arriba
        elif step == 'check_dependencies':
            if args.skip_validation:
                print("⏭️  Saltando validación de dependencias")
                steps_results[step] = True
            else:
                steps_results[step] = validate_dependencies()
        elif step == 'install_dependencies':
            if args.skip_install:
                print("⏭️  Saltando instalación de dependencias")
                steps_results[step] = True
            else:
                steps_results[step] = install_dependencies(args.environment)
        elif step == 'setup_database':
            steps_results[step] = setup_database()
        elif step == 'setup_redis':
            steps_results[step] = setup_redis()
        elif step == 'configure_environment':
            steps_results[step] = configure_environment()
        elif step == 'test_system':
            steps_results[step] = test_system()
        elif step == 'start_services':
            steps_results[step] = start_services()
        
        # Pausa entre pasos
        if not args.dry_run:
            time.sleep(1)
    
    # Generar y mostrar reporte
    print("\n" + "="*80)
    report = generate_deployment_report(steps_results)
    print_deployment_report(report)
    
    # Guardar reporte
    save_deployment_report(report)
    
    # Código de salida
    sys.exit(0 if report['overall_success'] else 1)

if __name__ == "__main__":
    main()
