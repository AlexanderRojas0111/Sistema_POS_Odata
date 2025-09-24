#!/usr/bin/env python3
"""
Script de validación de dependencias para Sistema POS Odata
Verifica que todas las librerías estén correctamente instaladas y sean compatibles
"""

import sys
import subprocess
import importlib
import importlib.metadata
from pathlib import Path
from typing import Dict, List, Tuple
import json

# Versiones mínimas requeridas
MINIMUM_VERSIONS = {
    'python': '3.13.0',
    'Flask': '3.1.0',
    'SQLAlchemy': '2.0.0',
    'psycopg2-binary': '2.9.0',
    'redis': '6.0.0',
    'celery': '5.5.0',
    'pydantic': '2.0.0',
    'torch': '2.0.0',
    'transformers': '4.0.0',
    'langchain': '0.3.0',
}

# Dependencias críticas que deben estar instaladas
CRITICAL_DEPS = [
    'Flask',
    'Flask-SQLAlchemy', 
    'Flask-JWT-Extended',
    'psycopg2-binary',
    'SQLAlchemy',
    'redis',
    'celery',
    'pydantic',
    'bcrypt',
    'PyJWT',
    'requests',
    'python-dotenv'
]

# Dependencias opcionales pero recomendadas
OPTIONAL_DEPS = [
    'torch',
    'transformers',
    'langchain',
    'sentence-transformers',
    'scikit-learn',
    'numpy',
    'pandas',
    'prometheus_client',
    'psutil'
]

def get_python_version() -> str:
    """Obtiene la versión de Python"""
    return sys.version

def check_python_version() -> Tuple[bool, str]:
    """Verifica que la versión de Python sea compatible"""
    version = sys.version_info
    min_version = tuple(map(int, MINIMUM_VERSIONS['python'].split('.')))
    
    if version >= min_version:
        return True, f"Python {version.major}.{version.minor}.{version.micro} ✓"
    else:
        return False, f"Python {version.major}.{version.minor}.{version.micro} ✗ (Requiere {MINIMUM_VERSIONS['python']}+)"

def get_installed_packages() -> Dict[str, str]:
    """Obtiene todas las librerías instaladas"""
    try:
        return {dist.metadata['Name']: dist.version for dist in importlib.metadata.distributions()}
    except Exception:
        # Fallback para versiones más antiguas de Python
        try:
            import pkg_resources
            return {dist.project_name: dist.version for dist in pkg_resources.working_set}
        except ImportError:
            return {}

def check_package_version(package_name: str, installed_version: str, min_version: str) -> Tuple[bool, str]:
    """Verifica que una librería tenga la versión mínima requerida"""
    try:
        from packaging import version
        installed = version.parse(installed_version)
        required = version.parse(min_version)
        
        if installed >= required:
            return True, f"{package_name} {installed_version} ✓"
        else:
            return False, f"{package_name} {installed_version} ✗ (Requiere {min_version}+)"
    except ImportError:
        # Fallback simple si packaging no está disponible
        return True, f"{package_name} {installed_version} ✓"

def check_critical_dependencies(installed_packages: Dict[str, str]) -> List[Tuple[bool, str]]:
    """Verifica las dependencias críticas"""
    results = []
    
    for dep in CRITICAL_DEPS:
        if dep in installed_packages:
            version = installed_packages[dep]
            min_version = MINIMUM_VERSIONS.get(dep, '0.0.0')
            status, message = check_package_version(dep, version, min_version)
            results.append((status, message))
        else:
            results.append((False, f"{dep} ✗ (No instalado)"))
    
    return results

def check_optional_dependencies(installed_packages: Dict[str, str]) -> List[Tuple[bool, str]]:
    """Verifica las dependencias opcionales"""
    results = []
    
    for dep in OPTIONAL_DEPS:
        if dep in installed_packages:
            version = installed_packages[dep]
            min_version = MINIMUM_VERSIONS.get(dep, '0.0.0')
            status, message = check_package_version(dep, version, min_version)
            results.append((status, message))
        else:
            results.append((False, f"{dep} ✗ (No instalado)"))
    
    return results

def test_imports() -> List[Tuple[bool, str]]:
    """Prueba la importación de librerías críticas"""
    results = []
    
    # Mapeo de nombres de paquetes a nombres de importación correctos
    import_mapping = {
        'Flask': 'flask',
        'Flask-SQLAlchemy': 'flask_sqlalchemy',
        'Flask-JWT-Extended': 'flask_jwt_extended',
        'psycopg2-binary': 'psycopg2',
        'SQLAlchemy': 'sqlalchemy',
        'redis': 'redis',
        'celery': 'celery',
        'pydantic': 'pydantic',
        'bcrypt': 'bcrypt',
        'PyJWT': 'jwt',
        'requests': 'requests',
        'python-dotenv': 'dotenv'
    }
    
    for dep in CRITICAL_DEPS:
        try:
            import_name = import_mapping.get(dep, dep.lower().replace('-', '_'))
            importlib.import_module(import_name)
            results.append((True, f"Import {dep} ✓"))
        except ImportError as e:
            results.append((False, f"Import {dep} ✗ ({str(e)})"))
    
    return results

def check_database_connection() -> Tuple[bool, str]:
    """Verifica la conexión a la base de datos"""
    try:
        import psycopg2
        return True, "Database driver psycopg2 ✓"
    except ImportError:
        return False, "Database driver psycopg2 ✗ (No instalado)"
    except Exception as e:
        return False, f"Database connection ✗ ({str(e)})"

def check_redis_connection() -> Tuple[bool, str]:
    """Verifica la conexión a Redis"""
    try:
        import redis
        return True, "Redis driver ✓"
    except ImportError:
        return False, "Redis driver ✗ (No instalado)"
    except Exception as e:
        return False, f"Redis connection ✗ ({str(e)})"

def generate_report() -> Dict:
    """Genera un reporte completo de validación"""
    python_status, python_message = check_python_version()
    installed_packages = get_installed_packages()
    
    critical_results = check_critical_dependencies(installed_packages)
    optional_results = check_optional_dependencies(installed_packages)
    import_results = test_imports()
    db_status, db_message = check_database_connection()
    redis_status, redis_message = check_redis_connection()
    
    # Calcular estadísticas
    critical_passed = sum(1 for status, _ in critical_results if status)
    critical_total = len(critical_results)
    optional_passed = sum(1 for status, _ in optional_results if status)
    optional_total = len(optional_results)
    
    report = {
        'timestamp': str(importlib.metadata.version('pip') if importlib.metadata.version('pip') else 'unknown'),
        'python_version': get_python_version(),
        'python_compatible': python_status,
        'python_message': python_message,
        'critical_dependencies': {
            'total': critical_total,
            'passed': critical_passed,
            'failed': critical_total - critical_passed,
            'results': [{'status': status, 'message': msg} for status, msg in critical_results]
        },
        'optional_dependencies': {
            'total': optional_total,
            'passed': optional_passed,
            'failed': optional_total - optional_passed,
            'results': [{'status': status, 'message': msg} for status, msg in optional_results]
        },
        'import_tests': [{'status': status, 'message': msg} for status, msg in import_results],
        'database': {'status': db_status, 'message': db_message},
        'redis': {'status': redis_status, 'message': redis_message},
        'overall_status': python_status and critical_passed == critical_total
    }
    
    return report

def print_report(report: Dict):
    """Imprime el reporte de validación en consola"""
    print("=" * 80)
    print("SISTEMA POS ODATA - VALIDACIÓN DE DEPENDENCIAS")
    print("=" * 80)
    print()
    
    # Python Version
    print(f"🐍 Python: {report['python_message']}")
    print()
    
    # Critical Dependencies
    print("🔴 DEPENDENCIAS CRÍTICAS:")
    print(f"   Total: {report['critical_dependencies']['total']}")
    print(f"   Pasadas: {report['critical_dependencies']['passed']}")
    print(f"   Fallidas: {report['critical_dependencies']['failed']}")
    print()
    
    for result in report['critical_dependencies']['results']:
        print(f"   {result['message']}")
    print()
    
    # Optional Dependencies
    print("🟡 DEPENDENCIAS OPCIONALES:")
    print(f"   Total: {report['optional_dependencies']['total']}")
    print(f"   Pasadas: {report['optional_dependencies']['passed']}")
    print(f"   Fallidas: {report['optional_dependencies']['failed']}")
    print()
    
    for result in report['optional_dependencies']['results']:
        print(f"   {result['message']}")
    print()
    
    # Import Tests
    print("📦 PRUEBAS DE IMPORTACIÓN:")
    for result in report['import_tests']:
        print(f"   {result['message']}")
    print()
    
    # Database & Redis
    print("🗄️  CONEXIONES:")
    print(f"   Base de datos: {report['database']['message']}")
    print(f"   Redis: {report['redis']['message']}")
    print()
    
    # Overall Status
    if report['overall_status']:
        print("✅ SISTEMA LISTO PARA DESPLIEGUE")
    else:
        print("❌ SISTEMA NO LISTO - REVISAR DEPENDENCIAS")
    
    print("=" * 80)

def save_report(report: Dict, filename: str = "dependency_validation_report.json"):
    """Guarda el reporte en un archivo JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"📄 Reporte guardado en: {filename}")
    except Exception as e:
        print(f"❌ Error al guardar reporte: {e}")

def main():
    """Función principal"""
    try:
        print("🔍 Iniciando validación de dependencias...")
        print()
        
        # Generar reporte
        report = generate_report()
        
        # Imprimir reporte
        print_report(report)
        
        # Guardar reporte
        save_report(report)
        
        # Código de salida
        sys.exit(0 if report['overall_status'] else 1)
        
    except Exception as e:
        print(f"❌ Error durante la validación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
