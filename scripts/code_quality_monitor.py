#!/usr/bin/env python3
"""
Code Quality Monitor - Sistema POS Sabrositas
=============================================
Script para monitoreo continuo de calidad de código
"""

import subprocess
import sys
import json
import os
import re
from datetime import datetime
from pathlib import Path

def run_flake8_analysis():
    """Ejecutar análisis de Flake8"""
    print("🔍 ANÁLISIS DE FLAKE8")
    print("-" * 40)
    
    try:
        # Ejecutar flake8 con configuración específica
        result = subprocess.run([
            'flake8', 'app/', 
            '--select=E501,W293,E302,E303,W391',
            '--statistics',
            '--count'
        ], capture_output=True, text=True)
        
        violations = 0
        if result.stdout:
            # Extraer número de violaciones
            lines = result.stdout.strip().split('\n')
            for line in lines:
                if line.strip() and line.strip().isdigit():
                    violations += int(line.strip())
        
        print(f"📊 Violaciones de estilo: {violations}")
        
        return {
            'violations': violations,
            'status': 'PASSED' if violations < 50 else 'WARNING' if violations < 100 else 'FAILED'
        }
        
    except FileNotFoundError:
        print("⚠️ Flake8 no instalado")
        return {'violations': 0, 'status': 'SKIPPED'}
    except Exception as e:
        print(f"❌ Error en Flake8: {e}")
        return {'violations': 999, 'status': 'ERROR'}

def run_radon_complexity():
    """Ejecutar análisis de complejidad con Radon"""
    print(f"\n🧮 ANÁLISIS DE COMPLEJIDAD")
    print("-" * 40)
    
    try:
        # Análisis de complejidad ciclomática
        result = subprocess.run([
            'radon', 'cc', 'app/', '-a', '-nc', '--total-average'
        ], capture_output=True, text=True)
        
        average_complexity = 0.0
        complex_functions = []
        
        if result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'Average complexity:' in line:
                    # Extraer complejidad promedio
                    match = re.search(r'Average complexity: \w+ \((\d+\.\d+)\)', line)
                    if match:
                        average_complexity = float(match.group(1))
                elif ' - ' in line and ('C' in line or 'D' in line or 'E' in line or 'F' in line):
                    # Funciones complejas
                    complex_functions.append(line.strip())
        
        print(f"📊 Complejidad promedio: {average_complexity:.2f}")
        print(f"📊 Funciones complejas: {len(complex_functions)}")
        
        status = 'PASSED'
        if average_complexity > 10 or len(complex_functions) > 5:
            status = 'FAILED'
        elif average_complexity > 5 or len(complex_functions) > 2:
            status = 'WARNING'
        
        return {
            'average': average_complexity,
            'complex_functions': complex_functions[:10],  # Máximo 10
            'status': status
        }
        
    except FileNotFoundError:
        print("⚠️ Radon no instalado")
        return {'average': 0, 'complex_functions': [], 'status': 'SKIPPED'}
    except Exception as e:
        print(f"❌ Error en Radon: {e}")
        return {'average': 999, 'complex_functions': [], 'status': 'ERROR'}

def check_function_length():
    """Verificar longitud de funciones"""
    print(f"\n📏 ANÁLISIS DE LONGITUD DE FUNCIONES")
    print("-" * 40)
    
    long_functions = []
    
    try:
        # Buscar archivos Python
        for py_file in Path('app').rglob('*.py'):
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            current_function = None
            function_start = 0
            indent_level = 0
            
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Detectar inicio de función
                if stripped.startswith('def ') and ':' in stripped:
                    if current_function:
                        # Finalizar función anterior
                        length = i - function_start - 1
                        if length > 50:  # Umbral de líneas
                            long_functions.append({
                                'file': str(py_file),
                                'function': current_function,
                                'lines': length,
                                'start_line': function_start
                            })
                    
                    current_function = stripped.split('(')[0].replace('def ', '')
                    function_start = i
                    indent_level = len(line) - len(line.lstrip())
            
            # Verificar última función
            if current_function:
                length = len(lines) - function_start
                if length > 50:
                    long_functions.append({
                        'file': str(py_file),
                        'function': current_function,
                        'lines': length,
                        'start_line': function_start
                    })
        
        print(f"📊 Funciones largas (>50 líneas): {len(long_functions)}")
        
        for func in long_functions[:5]:  # Mostrar máximo 5
            print(f"   - {func['function']} ({func['lines']} líneas) en {func['file']}")
        
        status = 'PASSED' if len(long_functions) == 0 else 'WARNING' if len(long_functions) < 5 else 'FAILED'
        
        return {
            'count': len(long_functions),
            'long_functions': long_functions[:10],
            'status': status
        }
        
    except Exception as e:
        print(f"❌ Error analizando longitud: {e}")
        return {'count': 0, 'long_functions': [], 'status': 'ERROR'}

def check_todos():
    """Verificar TODOs pendientes"""
    print(f"\n📝 VERIFICANDO TODOS PENDIENTES")
    print("-" * 40)
    
    try:
        result = subprocess.run([
            'grep', '-r', 'TODO\\|FIXME\\|XXX\\|HACK', 'app/',
            '--exclude-dir=__pycache__'
        ], capture_output=True, text=True)
        
        todos = []
        if result.stdout:
            todos = result.stdout.strip().split('\n')
            todos = [todo for todo in todos if todo.strip()]
        
        print(f"📊 TODOs encontrados: {len(todos)}")
        
        for todo in todos[:5]:  # Mostrar máximo 5
            print(f"   - {todo[:80]}...")
        
        status = 'PASSED' if len(todos) == 0 else 'WARNING' if len(todos) < 10 else 'FAILED'
        
        return {
            'count': len(todos),
            'todos': todos[:20],  # Máximo 20
            'status': status
        }
        
    except Exception as e:
        print(f"❌ Error verificando TODOs: {e}")
        return {'count': 0, 'todos': [], 'status': 'ERROR'}

def run_test_coverage():
    """Ejecutar tests y medir cobertura"""
    print(f"\n🧪 EJECUTANDO TESTS Y COBERTURA")
    print("-" * 40)
    
    try:
        # Verificar si hay tests
        tests_dir = Path('tests')
        if not tests_dir.exists():
            print("⚠️ Directorio tests no existe")
            return {'coverage': 0, 'tests_count': 0, 'status': 'SKIPPED'}
        
        test_files = list(tests_dir.glob('test_*.py'))
        print(f"📊 Archivos de test encontrados: {len(test_files)}")
        
        if len(test_files) == 0:
            print("⚠️ No se encontraron archivos de test")
            return {'coverage': 0, 'tests_count': 0, 'status': 'SKIPPED'}
        
        # Ejecutar tests con coverage (si está disponible)
        try:
            result = subprocess.run([
                'coverage', 'run', '--source=app', '-m', 'pytest', 'tests/', '-v'
            ], capture_output=True, text=True, timeout=60)
            
            # Obtener reporte de coverage
            coverage_result = subprocess.run([
                'coverage', 'report', '--format=json'
            ], capture_output=True, text=True)
            
            if coverage_result.returncode == 0:
                coverage_data = json.loads(coverage_result.stdout)
                total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0)
                print(f"📊 Cobertura total: {total_coverage:.1f}%")
                
                status = 'PASSED' if total_coverage >= 80 else 'WARNING' if total_coverage >= 60 else 'FAILED'
                
                return {
                    'coverage': total_coverage,
                    'tests_count': len(test_files),
                    'status': status
                }
            else:
                print("⚠️ Error obteniendo reporte de coverage")
                
        except subprocess.TimeoutExpired:
            print("⚠️ Tests tardaron demasiado tiempo")
        except FileNotFoundError:
            print("⚠️ Coverage no está instalado")
        
        # Fallback: ejecutar pytest simple
        try:
            result = subprocess.run([
                'python', '-m', 'pytest', 'tests/', '--tb=no', '-q'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ Tests básicos pasaron")
                return {'coverage': 50, 'tests_count': len(test_files), 'status': 'WARNING'}
            else:
                print("❌ Tests fallaron")
                return {'coverage': 0, 'tests_count': len(test_files), 'status': 'FAILED'}
                
        except:
            print("❌ No se pudieron ejecutar tests")
            return {'coverage': 0, 'tests_count': 0, 'status': 'ERROR'}
            
    except Exception as e:
        print(f"❌ Error ejecutando tests: {e}")
        return {'coverage': 0, 'tests_count': 0, 'status': 'ERROR'}

def generate_quality_report():
    """Generar reporte completo de calidad"""
    print(f"\n📊 GENERANDO REPORTE DE CALIDAD DE CÓDIGO")
    print("=" * 70)
    
    # Ejecutar todos los análisis
    flake8_results = run_flake8_analysis()
    complexity_results = run_radon_complexity()
    function_length_results = check_function_length()
    todos_results = check_todos()
    coverage_results = run_test_coverage()
    
    # Calcular puntuación general
    scores = {
        'flake8': 100 if flake8_results['status'] == 'PASSED' else 70 if flake8_results['status'] == 'WARNING' else 30,
        'complexity': 100 if complexity_results['status'] == 'PASSED' else 70 if complexity_results['status'] == 'WARNING' else 30,
        'function_length': 100 if function_length_results['status'] == 'PASSED' else 70 if function_length_results['status'] == 'WARNING' else 30,
        'todos': 100 if todos_results['status'] == 'PASSED' else 80 if todos_results['status'] == 'WARNING' else 40,
        'coverage': coverage_results['coverage'] if coverage_results['status'] != 'ERROR' else 0
    }
    
    overall_score = sum(scores.values()) / len(scores)
    
    # Determinar estado general
    if overall_score >= 85:
        overall_status = "EXCELLENT"
    elif overall_score >= 75:
        overall_status = "GOOD"
    elif overall_score >= 60:
        overall_status = "WARNING"
    else:
        overall_status = "FAILED"
    
    # Crear reporte completo
    report = {
        'timestamp': datetime.now().isoformat(),
        'system': 'Sistema POS Sabrositas',
        'version': '2.0.0',
        'overall': {
            'score': round(overall_score, 1),
            'status': overall_status
        },
        'metrics': {
            'style': flake8_results,
            'complexity': complexity_results,
            'function_length': function_length_results,
            'todos': todos_results,
            'coverage': coverage_results
        },
        'scores': scores
    }
    
    # Guardar reporte
    os.makedirs('reports', exist_ok=True)
    report_file = f"reports/code_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    latest_file = "reports/code_quality_report_latest.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    with open(latest_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Mostrar resumen
    status_emoji = "🎉" if overall_status == "EXCELLENT" else "✅" if overall_status == "GOOD" else "⚠️" if overall_status == "WARNING" else "❌"
    
    print(f"\n{status_emoji} ANÁLISIS DE CALIDAD COMPLETADO")
    print("=" * 60)
    print(f"Puntuación general: {overall_score:.1f}/100")
    print(f"Estado: {overall_status}")
    print(f"Reporte guardado: {report_file}")
    
    print(f"\n📊 DESGLOSE DE PUNTUACIONES:")
    for metric, score in scores.items():
        icon = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
        print(f"   {icon} {metric.replace('_', ' ').title()}: {score:.1f}")
    
    return overall_score >= 70

def main():
    """Función principal"""
    print("📊 MONITOR DE CALIDAD DE CÓDIGO")
    print("=" * 70)
    
    success = generate_quality_report()
    
    if success:
        print(f"\n🎊 CALIDAD DE CÓDIGO ACEPTABLE")
        exit(0)
    else:
        print(f"\n⚠️ CALIDAD DE CÓDIGO NECESITA MEJORA")
        exit(1)

if __name__ == "__main__":
    main()
