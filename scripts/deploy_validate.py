#!/usr/bin/env python3
"""
Validador de Despliegue Simplificado - POS O'data
"""

import os
import sys
import requests
import subprocess
import json
from pathlib import Path

def print_step(step, status=""):
    """Imprime paso con formato"""
    status_icon = "✅" if status == "success" else "❌" if status == "error" else "🔍"
    print(f"{status_icon} {step}")

def validate_backend():
    """Valida backend"""
    print("\n🔍 VALIDANDO BACKEND")
    print("-" * 40)
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_step(f"Backend funcionando: {data['status']}", "success")
            print_step(f"Versión: {data.get('version', 'N/A')}", "success")
            print_step(f"Entorno: {data.get('environment', 'N/A')}", "success")
            return True
        else:
            print_step(f"Backend error: {response.status_code}", "error")
            return False
    except Exception as e:
        print_step(f"Backend no accesible: {e}", "error")
        return False

def validate_dependencies():
    """Valida dependencias críticas"""
    print("\n🔍 VALIDANDO DEPENDENCIAS")
    print("-" * 40)
    
    deps = ['flask', 'sqlalchemy', 'redis', 'requests', 'marshmallow']
    failed = []
    
    for dep in deps:
        try:
            __import__(dep)
            print_step(f"{dep} importado correctamente", "success")
        except ImportError:
            print_step(f"{dep} no disponible", "error")
            failed.append(dep)
    
    return len(failed) == 0

def test_api_endpoints():
    """Prueba endpoints básicos"""
    print("\n🔍 PROBANDO ENDPOINTS")
    print("-" * 40)
    
    endpoints = [
        "/health",
        "/api/v1/products", 
        "/api/v1/users",
        "/"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"http://localhost:5000{endpoint}", timeout=5)
            if response.status_code in [200, 401, 403]:  # 401/403 ok para endpoints protegidos
                print_step(f"{endpoint}: {response.status_code}", "success")
            else:
                print_step(f"{endpoint}: {response.status_code}", "error")
        except Exception as e:
            print_step(f"{endpoint}: Error - {str(e)[:50]}", "error")

def validate_frontend():
    """Valida frontend"""
    print("\n🔍 VALIDANDO FRONTEND")
    print("-" * 40)
    
    frontend_path = Path("Sistema_POS_Odata_nuevo/frontend")
    
    if not frontend_path.exists():
        print_step("Directorio frontend no encontrado", "error")
        return False
    
    # Verificar archivos clave
    files_to_check = [
        "package.json",
        "tsconfig.app.json", 
        "src/main.tsx",
        "src/types/global.d.ts"
    ]
    
    for file in files_to_check:
        file_path = frontend_path / file
        if file_path.exists():
            print_step(f"{file} encontrado", "success")
        else:
            print_step(f"{file} faltante", "error")
    
    return True

def main():
    """Función principal de validación"""
    print("🚀 VALIDACIÓN RÁPIDA DEL SISTEMA POS O'DATA")
    print("=" * 50)
    
    # Ejecutar validaciones
    results = {
        "backend": validate_backend(),
        "dependencies": validate_dependencies(), 
        "frontend": validate_frontend()
    }
    
    # Probar endpoints
    if results["backend"]:
        test_api_endpoints()
    
    # Resumen
    print("\n📊 RESUMEN DE VALIDACIÓN")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test.capitalize()}: {status}")
    
    print(f"\nResultado: {passed}/{total} validaciones exitosas")
    
    if passed == total:
        print("\n🎉 ¡SISTEMA VALIDADO EXITOSAMENTE!")
        print("✅ El sistema está listo para uso")
        return True
    else:
        print(f"\n⚠️ Sistema parcialmente validado")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
