#!/usr/bin/env python3
"""
Script para generar reportes de calidad de código
"""

import os
import sys
import json
import subprocess
import datetime
from pathlib import Path

def run_command(command, description=""):
    """Ejecuta un comando y retorna el resultado"""
    print(f"🔍 {description}")
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            timeout=300
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout ejecutando comando"
    except Exception as e:
        return False, "", str(e)

def check_dependencies():
    """Verifica que las herramientas necesarias estén instaladas"""
    tools = {
        'flake8': 'python -m pip install flake8',
        'pytest': 'python -m pip install pytest pytest-cov',
        'bandit': 'python -m pip install bandit'
    }
    
    missing_tools = []
    
    for tool, install_cmd in tools.items():
        success, _, _ = run_command(f"python -m {tool} --version", f"Verificando {tool}")
        if not success:
            print(f"⚠️  {tool} no encontrado. Instalando...")
            success, _, _ = run_command(install_cmd, f"Instalando {tool}")
            if not success:
                missing_tools.append(tool)
    
    return len(missing_tools) == 0, missing_tools

def run_linting():
    """Ejecuta análisis de linting con flake8"""
    print("\n📋 ANÁLISIS DE LINTING")
    print("=" * 40)
    
    # Configuración de flake8
    flake8_config = """
[flake8]
max-line-length = 88
ignore = E203, W503, F401, E501
exclude = 
    .git,
    __pycache__,
    venv,
    .venv,
    migrations,
    node_modules
"""
    
    # Crear archivo de configuración temporal
    with open('.flake8', 'w') as f:
        f.write(flake8_config)
    
    success, stdout, stderr = run_command(
        "python -m flake8 app/ scripts/ --format=json", 
        "Ejecutando flake8"
    )
    
    issues = []
    if stdout:
        try:
            # flake8 con formato JSON puede no estar disponible
            issues = json.loads(stdout)
        except:
            # Parsear formato estándar
            lines = stdout.strip().split('\n')
            for line in lines:
                if line.strip():
                    parts = line.split(':')
                    if len(parts) >= 4:
                        issues.append({
                            'filename': parts[0],
                            'line_number': parts[1],
                            'column_number': parts[2],
                            'error_code': parts[3].split()[0],
                            'text': ':'.join(parts[3:]).strip()
                        })
    
    return {
        'tool': 'flake8',
        'success': success,
        'issues_count': len(issues),
        'issues': issues[:50],  # Limitar a 50 issues
        'stdout': stdout,
        'stderr': stderr
    }

def run_security_check():
    """Ejecuta análisis de seguridad con bandit"""
    print("\n🔒 ANÁLISIS DE SEGURIDAD")
    print("=" * 40)
    
    success, stdout, stderr = run_command(
        "python -m bandit -r app/ -f json", 
        "Ejecutando bandit"
    )
    
    issues = []
    if stdout:
        try:
            bandit_result = json.loads(stdout)
            issues = bandit_result.get('results', [])
        except:
            pass
    
    return {
        'tool': 'bandit',
        'success': success,
        'issues_count': len(issues),
        'issues': issues[:20],  # Limitar a 20 issues
        'stdout': stdout,
        'stderr': stderr
    }

def run_tests():
    """Ejecuta tests con pytest"""
    print("\n🧪 EJECUCIÓN DE TESTS")
    print("=" * 40)
    
    success, stdout, stderr = run_command(
        "python -m pytest tests/ -v --tb=short", 
        "Ejecutando pytest"
    )
    
    # Extraer estadísticas básicas
    test_stats = {
        'total': 0,
        'passed': 0,
        'failed': 0,
        'errors': 0
    }
    
    if stdout:
        lines = stdout.split('\n')
        for line in lines:
            if 'passed' in line or 'failed' in line or 'error' in line:
                if '::' in line:
                    test_stats['total'] += 1
                    if 'PASSED' in line:
                        test_stats['passed'] += 1
                    elif 'FAILED' in line:
                        test_stats['failed'] += 1
                    elif 'ERROR' in line:
                        test_stats['errors'] += 1
    
    return {
        'tool': 'pytest',
        'success': success,
        'stats': test_stats,
        'stdout': stdout,
        'stderr': stderr
    }

def generate_quality_report():
    """Genera el reporte de calidad completo"""
    print("🚀 GENERANDO REPORTE DE CALIDAD DE CÓDIGO")
    print("=" * 50)
    
    # Verificar dependencias
    deps_ok, missing = check_dependencies()
    if not deps_ok:
        print(f"❌ Herramientas faltantes: {missing}")
        return False
    
    # Crear directorio de reportes
    reports_dir = Path('reports')
    reports_dir.mkdir(exist_ok=True)
    
    # Ejecutar análisis
    linting_result = run_linting()
    security_result = run_security_check()
    test_result = run_tests()
    
    # Generar reporte JSON
    timestamp = datetime.datetime.now().isoformat()
    report = {
        'timestamp': timestamp,
        'version': '1.0.0',
        'project': 'Sistema_POS_Odata',
        'summary': {
            'linting_issues': linting_result['issues_count'],
            'security_issues': security_result['issues_count'],
            'test_stats': test_result['stats'],
            'overall_score': calculate_score(linting_result, security_result, test_result)
        },
        'details': {
            'linting': linting_result,
            'security': security_result,
            'testing': test_result
        }
    }
    
    # Guardar reporte JSON
    report_filename = f"code_quality_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    report_path = reports_dir / report_filename
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    # Generar reporte Markdown
    generate_markdown_report(report, reports_dir)
    
    print(f"\n✅ Reporte generado: {report_path}")
    print_summary(report)
    
    return True

def calculate_score(linting, security, testing):
    """Calcula un score general de calidad"""
    score = 100
    
    # Penalizar por issues de linting
    score -= min(linting['issues_count'] * 2, 30)
    
    # Penalizar por issues de seguridad
    score -= min(security['issues_count'] * 5, 40)
    
    # Penalizar por tests fallidos
    test_stats = testing['stats']
    if test_stats['total'] > 0:
        failure_rate = (test_stats['failed'] + test_stats['errors']) / test_stats['total']
        score -= failure_rate * 30
    
    return max(score, 0)

def generate_markdown_report(report, reports_dir):
    """Genera un reporte en formato Markdown"""
    
    markdown_content = f"""# Reporte de Calidad de Código

**Proyecto**: {report['project']}  
**Fecha**: {report['timestamp']}  
**Score General**: {report['summary']['overall_score']:.1f}/100

## 📊 Resumen

- **Issues de Linting**: {report['summary']['linting_issues']}
- **Issues de Seguridad**: {report['summary']['security_issues']}
- **Tests Totales**: {report['summary']['test_stats']['total']}
- **Tests Pasados**: {report['summary']['test_stats']['passed']}
- **Tests Fallidos**: {report['summary']['test_stats']['failed']}

## 🔍 Detalles

### Linting (flake8)
{f"✅ Sin issues encontrados" if report['details']['linting']['issues_count'] == 0 else f"⚠️ {report['details']['linting']['issues_count']} issues encontrados"}

### Seguridad (bandit)
{f"✅ Sin vulnerabilidades encontradas" if report['details']['security']['issues_count'] == 0 else f"🔒 {report['details']['security']['issues_count']} issues de seguridad encontrados"}

### Testing (pytest)
{f"✅ Todos los tests pasaron" if report['details']['testing']['stats']['failed'] == 0 else f"❌ {report['details']['testing']['stats']['failed']} tests fallaron"}

---
*Reporte generado automáticamente*
"""
    
    with open(reports_dir / 'coverage_report.md', 'w', encoding='utf-8') as f:
        f.write(markdown_content)

def print_summary(report):
    """Imprime un resumen del reporte"""
    print("\n📊 RESUMEN DEL REPORTE")
    print("=" * 30)
    print(f"Score General: {report['summary']['overall_score']:.1f}/100")
    print(f"Issues de Linting: {report['summary']['linting_issues']}")
    print(f"Issues de Seguridad: {report['summary']['security_issues']}")
    print(f"Tests: {report['summary']['test_stats']['passed']}/{report['summary']['test_stats']['total']} pasados")
    
    if report['summary']['overall_score'] >= 80:
        print("🎉 ¡Excelente calidad de código!")
    elif report['summary']['overall_score'] >= 60:
        print("👍 Buena calidad de código")
    else:
        print("⚠️ Se necesita mejorar la calidad del código")

if __name__ == '__main__':
    success = generate_quality_report()
    sys.exit(0 if success else 1)
