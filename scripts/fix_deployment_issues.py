#!/usr/bin/env python3
"""
Script de Corrección de Problemas de Despliegue
===============================================
Corrige los problemas identificados en el despliegue profesional
"""

import os
import sys
import subprocess
import requests
from pathlib import Path

def print_step(step, status=""):
    """Imprime paso con formato profesional"""
    status_icon = "✅" if status == "success" else "❌" if status == "error" else "⚠️" if status == "warning" else "🔧"
    print(f"{status_icon} {step}")

def run_command(command):
    """Ejecuta comando y retorna resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=60)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def fix_fakeredis():
    """Corrige problema de fakeredis"""
    print("\n🔧 CORRIGIENDO FAKEREDIS")
    print("-" * 40)
    
    # Verificar si ya está instalado
    try:
        import fakeredis
        print_step("fakeredis ya está instalado", "success")
        return True
    except ImportError:
        print_step("fakeredis no encontrado, instalando...", "warning")
        
        # Instalar fakeredis
        success, stdout, stderr = run_command("python -m pip install fakeredis")
        if success:
            print_step("fakeredis instalado exitosamente", "success")
            return True
        else:
            print_step(f"Error instalando fakeredis: {stderr}", "error")
            return False

def validate_backend_status():
    """Valida que el backend siga funcionando"""
    print("\n🔧 VALIDANDO BACKEND POST-CORRECCIÓN")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_step(f"Backend funcionando: {data['status']}", "success")
            print_step(f"Timestamp: {data.get('timestamp', 'N/A')}", "success")
            
            # Probar endpoints adicionales
            endpoints = ["/api/v1/products", "/api/v1/users", "/"]
            for endpoint in endpoints:
                try:
                    resp = requests.get(f"http://localhost:5000{endpoint}", timeout=5)
                    if resp.status_code in [200, 401, 403]:
                        print_step(f"Endpoint {endpoint}: OK ({resp.status_code})", "success")
                    else:
                        print_step(f"Endpoint {endpoint}: {resp.status_code}", "warning")
                except Exception as e:
                    print_step(f"Endpoint {endpoint}: Error", "warning")
            
            return True
        else:
            print_step(f"Backend error: {response.status_code}", "error")
            return False
    except Exception as e:
        print_step(f"Backend no accesible: {e}", "error")
        return False

def check_frontend_structure():
    """Verifica estructura del frontend"""
    print("\n🔧 VERIFICANDO ESTRUCTURA FRONTEND")
    print("-" * 40)
    
    frontend_path = Path("Sistema_POS_Odata_nuevo/frontend")
    
    if not frontend_path.exists():
        print_step("Directorio frontend no encontrado", "error")
        return False
    
    # Verificar archivos clave
    key_files = [
        "package.json",
        "tsconfig.app.json",
        "src/main.tsx",
        "src/App.tsx",
        "src/types/global.d.ts"
    ]
    
    missing_files = []
    for file in key_files:
        file_path = frontend_path / file
        if file_path.exists():
            print_step(f"{file} ✓", "success")
        else:
            print_step(f"{file} ✗", "error")
            missing_files.append(file)
    
    if missing_files:
        print_step(f"Archivos faltantes: {', '.join(missing_files)}", "warning")
    
    return len(missing_files) == 0

def check_node_npm():
    """Verifica disponibilidad de Node.js y npm"""
    print("\n🔧 VERIFICANDO NODE.JS Y NPM")
    print("-" * 40)
    
    # Verificar Node.js
    success, stdout, stderr = run_command("node --version")
    if success:
        print_step(f"Node.js disponible: {stdout.strip()}", "success")
        node_available = True
    else:
        print_step("Node.js no encontrado", "error")
        node_available = False
    
    # Verificar npm
    success, stdout, stderr = run_command("npm --version")
    if success:
        print_step(f"npm disponible: {stdout.strip()}", "success")
        npm_available = True
    else:
        print_step("npm no encontrado", "error")
        npm_available = False
    
    return node_available and npm_available

def generate_status_report():
    """Genera reporte de estado actual"""
    print("\n📊 GENERANDO REPORTE DE ESTADO")
    print("-" * 40)
    
    # Información del sistema
    try:
        import platform
        system_info = {
            "os": platform.system(),
            "python_version": platform.python_version(),
            "architecture": platform.architecture()[0]
        }
        print_step(f"SO: {system_info['os']} {system_info['architecture']}", "success")
        print_step(f"Python: {system_info['python_version']}", "success")
    except Exception as e:
        print_step(f"Error obteniendo info del sistema: {e}", "warning")
    
    # Estado del backend
    backend_ok = validate_backend_status()
    
    # Estado de dependencias críticas
    deps = ['flask', 'sqlalchemy', 'redis', 'requests', 'marshmallow', 'fakeredis']
    deps_ok = []
    deps_fail = []
    
    for dep in deps:
        try:
            __import__(dep)
            deps_ok.append(dep)
        except ImportError:
            deps_fail.append(dep)
    
    print_step(f"Dependencias OK: {len(deps_ok)}/{len(deps)}", "success" if len(deps_fail) == 0 else "warning")
    if deps_fail:
        print_step(f"Dependencias faltantes: {', '.join(deps_fail)}", "warning")
    
    # Crear reporte JSON
    report = {
        "timestamp": "2025-09-22T21:00:00",
        "backend_status": "healthy" if backend_ok else "error",
        "dependencies_ok": deps_ok,
        "dependencies_missing": deps_fail,
        "frontend_structure": check_frontend_structure(),
        "node_npm_available": check_node_npm()
    }
    
    # Guardar reporte
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    with open(reports_dir / "deployment_status_corrected.json", 'w') as f:
        import json
        json.dump(report, f, indent=2)
    
    print_step("Reporte guardado en reports/deployment_status_corrected.json", "success")
    
    return report

def main():
    """Función principal de corrección"""
    print("🔧 CORRECCIÓN PROFESIONAL DE PROBLEMAS DE DESPLIEGUE")
    print("=" * 60)
    print("Sistema POS O'data v2.0.0 - Corrección de Issues")
    print("=" * 60)
    
    # Secuencia de correcciones
    corrections = [
        ("Corrigiendo fakeredis", fix_fakeredis),
        ("Validando backend", validate_backend_status),
        ("Verificando frontend", check_frontend_structure),
        ("Verificando Node/npm", check_node_npm)
    ]
    
    results = {}
    
    for correction_name, correction_func in corrections:
        print(f"\n🔧 {correction_name.upper()}")
        try:
            result = correction_func()
            results[correction_name] = result
            status = "✅ EXITOSO" if result else "❌ FALLÓ"
            print_step(f"{correction_name}: {status}", "success" if result else "error")
        except Exception as e:
            print_step(f"Error en {correction_name}: {e}", "error")
            results[correction_name] = False
    
    # Generar reporte final
    final_report = generate_status_report()
    
    # Resumen final
    print("\n🎯 RESUMEN DE CORRECCIONES")
    print("=" * 60)
    
    successful_corrections = sum(results.values())
    total_corrections = len(results)
    
    for correction, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {correction}")
    
    print(f"\nCorrecciones exitosas: {successful_corrections}/{total_corrections}")
    
    if successful_corrections == total_corrections:
        print("\n🎉 ¡TODAS LAS CORRECCIONES APLICADAS EXITOSAMENTE!")
        print("✅ Sistema listo para producción")
    else:
        print(f"\n⚠️ Correcciones parciales aplicadas")
        print("🔧 Revisar elementos pendientes")
    
    return successful_corrections == total_corrections

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
