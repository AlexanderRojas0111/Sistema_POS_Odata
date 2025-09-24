#!/usr/bin/env python3
"""
Script para validar el frontend y generar reportes
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command, cwd=None):
    """Ejecuta un comando y retorna el resultado"""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True,
            cwd=cwd,
            timeout=300
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Timeout ejecutando comando"
    except Exception as e:
        return False, "", str(e)

def validate_frontend():
    """Valida el frontend React"""
    
    frontend_path = Path('Sistema_POS_Odata_nuevo/frontend')
    
    if not frontend_path.exists():
        print("❌ Directorio del frontend no encontrado")
        return False
    
    print("🔍 VALIDANDO FRONTEND REACT")
    print("=" * 40)
    
    # Verificar package.json
    package_json = frontend_path / 'package.json'
    if not package_json.exists():
        print("❌ package.json no encontrado")
        return False
    
    print("✅ package.json encontrado")
    
    # Verificar node_modules
    node_modules = frontend_path / 'node_modules'
    if not node_modules.exists():
        print("⚠️  node_modules no encontrado, instalando dependencias...")
        success, stdout, stderr = run_command('npm install', cwd=frontend_path)
        if not success:
            print(f"❌ Error instalando dependencias: {stderr}")
            return False
        print("✅ Dependencias instaladas")
    else:
        print("✅ node_modules encontrado")
    
    # Verificar TypeScript
    print("\n🔍 Verificando TypeScript...")
    success, stdout, stderr = run_command('npx tsc --noEmit', cwd=frontend_path)
    if success:
        print("✅ TypeScript: Sin errores de tipos")
    else:
        print("⚠️  TypeScript: Errores encontrados")
        print(f"Detalles: {stderr}")
    
    # Verificar ESLint
    print("\n🔍 Verificando ESLint...")
    success, stdout, stderr = run_command('npx eslint src/ --ext .ts,.tsx --format json', cwd=frontend_path)
    
    eslint_issues = 0
    if stdout:
        try:
            eslint_results = json.loads(stdout)
            for file_result in eslint_results:
                eslint_issues += len(file_result.get('messages', []))
        except:
            pass
    
    print(f"ESLint: {eslint_issues} issues encontrados")
    
    # Intentar build
    print("\n🔍 Intentando build de producción...")
    success, stdout, stderr = run_command('npm run build', cwd=frontend_path)
    if success:
        print("✅ Build de producción exitoso")
    else:
        print("❌ Error en build de producción")
        print(f"Detalles: {stderr}")
        return False
    
    # Generar reporte
    report = {
        "timestamp": "2025-09-22",
        "frontend_validation": {
            "package_json": True,
            "dependencies_installed": True,
            "typescript_check": success,
            "eslint_issues": eslint_issues,
            "build_success": success
        }
    }
    
    # Crear directorio de reportes si no existe
    reports_dir = Path('reports')
    reports_dir.mkdir(exist_ok=True)
    
    with open(reports_dir / 'frontend_validation.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📊 Reporte guardado en reports/frontend_validation.json")
    
    return True

def main():
    """Función principal"""
    print("🚀 VALIDACIÓN DEL FRONTEND")
    print("=" * 50)
    
    success = validate_frontend()
    
    if success:
        print("\n🎉 ¡Validación del frontend completada!")
    else:
        print("\n❌ Validación del frontend falló")
    
    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
