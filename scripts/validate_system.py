#!/usr/bin/env python3
"""
System Validation Script - Sistema POS Sabrositas
=================================================
Script para validación completa del sistema
"""

import subprocess
import sys
import json
import os
import requests
from datetime import datetime
from pathlib import Path

def validate_backend():
    """Validar backend del sistema"""
    print("🔧 VALIDANDO BACKEND")
    print("-" * 40)
    
    try:
        # Verificar que el servidor responde
        response = requests.get('http://localhost:8000/api/v1/health', timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend funcionando")
            print(f"   Status: {data.get('status', 'N/A')}")
            print(f"   Database: {data.get('database', 'N/A')}")
            print(f"   Version: {data.get('version', 'N/A')}")
            return True
        else:
            print(f"❌ Backend error {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Backend no está ejecutándose")
        return False
    except Exception as e:
        print(f"❌ Error validando backend: {e}")
        return False

def validate_database():
    """Validar conexión y estructura de base de datos"""
    print(f"\n💾 VALIDANDO BASE DE DATOS")
    print("-" * 40)
    
    try:
        # Verificar que el archivo de BD existe
        db_file = Path("instance/pos_odata.db")
        if db_file.exists():
            print(f"✅ Archivo de base de datos existe ({db_file.stat().st_size} bytes)")
            
            # Verificar endpoints que requieren BD
            try:
                response = requests.get('http://localhost:8000/api/v1/products', timeout=5)
                if response.status_code == 200:
                    products = response.json()
                    print(f"✅ Productos en BD: {len(products.get('data', []))}")
                    return True
                else:
                    print(f"⚠️ Error consultando productos: {response.status_code}")
                    return False
            except:
                print("⚠️ No se puede conectar para verificar datos")
                return False
        else:
            print("❌ Archivo de base de datos no existe")
            return False
            
    except Exception as e:
        print(f"❌ Error validando base de datos: {e}")
        return False

def validate_frontend_build():
    """Validar que el frontend se puede construir"""
    print(f"\n🎨 VALIDANDO FRONTEND")
    print("-" * 40)
    
    try:
        frontend_dir = Path("frontend")
        if not frontend_dir.exists():
            print("❌ Directorio frontend no existe")
            return False
        
        # Verificar package.json
        package_json = frontend_dir / "package.json"
        if package_json.exists():
            print("✅ package.json encontrado")
            
            # Verificar si node_modules existe
            node_modules = frontend_dir / "node_modules"
            if node_modules.exists():
                print("✅ Dependencias instaladas")
                return True
            else:
                print("⚠️ node_modules no existe - ejecutar npm install")
                return False
        else:
            print("❌ package.json no encontrado")
            return False
            
    except Exception as e:
        print(f"❌ Error validando frontend: {e}")
        return False

def validate_configuration():
    """Validar archivos de configuración"""
    print(f"\n⚙️ VALIDANDO CONFIGURACIÓN")
    print("-" * 40)
    
    config_files = [
        'requirements.txt',
        'requirements-dev.txt',
        'main.py',
        'frontend/package.json',
        'frontend/tsconfig.json',
        '.github/workflows/ci-cd.yml'
    ]
    
    missing_files = []
    existing_files = []
    
    for config_file in config_files:
        if Path(config_file).exists():
            existing_files.append(config_file)
        else:
            missing_files.append(config_file)
    
    print(f"✅ Archivos existentes: {len(existing_files)}")
    for file in existing_files:
        print(f"   - {file}")
    
    if missing_files:
        print(f"❌ Archivos faltantes: {len(missing_files)}")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    return True

def validate_api_endpoints():
    """Validar endpoints críticos de la API"""
    print(f"\n🌐 VALIDANDO ENDPOINTS DE API")
    print("-" * 40)
    
    critical_endpoints = [
        '/api/v1/health',
        '/api/v1/products',
        '/api/v1/sales/stats',
        '/api/v1/reports-final/health',
        '/api/v1/reports-final/sales'
    ]
    
    working_endpoints = []
    failed_endpoints = []
    
    for endpoint in critical_endpoints:
        try:
            response = requests.get(f'http://localhost:8000{endpoint}', timeout=5)
            
            if response.status_code in [200, 401, 403]:  # 401/403 son OK (requieren auth)
                working_endpoints.append(endpoint)
                status = "✅" if response.status_code == 200 else "🔐"
                print(f"   {status} {endpoint}")
            else:
                failed_endpoints.append(endpoint)
                print(f"   ❌ {endpoint} (error {response.status_code})")
                
        except Exception as e:
            failed_endpoints.append(endpoint)
            print(f"   ❌ {endpoint} (error: {str(e)[:50]})")
    
    success_rate = len(working_endpoints) / len(critical_endpoints) * 100
    print(f"\n📊 Tasa de éxito de endpoints: {success_rate:.1f}%")
    
    return success_rate >= 80

def generate_validation_report():
    """Generar reporte completo de validación"""
    print(f"\n📋 GENERANDO REPORTE DE VALIDACIÓN")
    print("-" * 40)
    
    # Ejecutar todas las validaciones
    validations = {
        'backend': validate_backend(),
        'database': validate_database(),
        'frontend': validate_frontend_build(),
        'configuration': validate_configuration(),
        'api_endpoints': validate_api_endpoints()
    }
    
    # Calcular puntuación general
    passed = sum(validations.values())
    total = len(validations)
    score = (passed / total) * 100
    
    # Determinar estado
    if score >= 90:
        status = "EXCELLENT"
        emoji = "🎉"
    elif score >= 80:
        status = "GOOD"
        emoji = "✅"
    elif score >= 70:
        status = "WARNING"
        emoji = "⚠️"
    else:
        status = "FAILED"
        emoji = "❌"
    
    # Crear reporte
    report = {
        'timestamp': datetime.now().isoformat(),
        'system': 'Sistema POS Sabrositas',
        'version': '2.0.0',
        'validations': validations,
        'score': score,
        'status': status,
        'passed_checks': passed,
        'total_checks': total
    }
    
    # Guardar reporte
    os.makedirs('reports', exist_ok=True)
    report_file = f"reports/system_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Mostrar resumen
    print(f"\n{emoji} VALIDACIÓN DEL SISTEMA COMPLETADA")
    print("=" * 60)
    print(f"Estado: {status}")
    print(f"Puntuación: {score:.1f}%")
    print(f"Verificaciones pasadas: {passed}/{total}")
    print(f"Reporte guardado: {report_file}")
    
    # Mostrar detalles
    print(f"\n📊 DETALLES:")
    for check, result in validations.items():
        status_icon = "✅" if result else "❌"
        print(f"   {status_icon} {check.replace('_', ' ').title()}")
    
    return score >= 80

def main():
    """Función principal"""
    print("🔍 VALIDACIÓN COMPLETA DEL SISTEMA")
    print("=" * 70)
    
    success = generate_validation_report()
    
    if success:
        print(f"\n🎊 SISTEMA VALIDADO EXITOSAMENTE")
        exit(0)
    else:
        print(f"\n⚠️ SISTEMA NECESITA ATENCIÓN")
        exit(1)

if __name__ == "__main__":
    main()
