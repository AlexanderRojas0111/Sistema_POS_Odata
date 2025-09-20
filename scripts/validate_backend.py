#!/usr/bin/env python3
"""
Script de validación del backend
Sistema POS O'Data v2.0.0
"""

import requests
import json
import sys
from datetime import datetime
import os

def test_backend_health():
    print('🔍 VERIFICANDO ESTADO DEL BACKEND')
    print('=' * 50)
    
    base_url = 'http://localhost:8000'
    endpoints_to_test = [
        '/api/v1/health',
        '/api/v1/auth/health', 
        '/api/v1/products',
        '/api/v1/sales',
        '/api/v1/users',
        '/api/v1/reports-final/health',
        '/api/v1/dashboard/summary'
    ]
    
    results = {
        'working': [],
        'not_working': [],
        'errors': []
    }
    
    for endpoint in endpoints_to_test:
        try:
            url = f'{base_url}{endpoint}'
            print(f'Testing: {endpoint}', end=' ... ')
            
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                print('✅ OK')
                results['working'].append(endpoint)
            elif response.status_code in [401, 403]:
                print('🔒 AUTH REQUIRED')
                results['working'].append(f'{endpoint} (auth required)')
            else:
                print(f'❌ ERROR {response.status_code}')
                results['not_working'].append(f'{endpoint} ({response.status_code})')
                
        except requests.exceptions.ConnectionError:
            print('❌ CONNECTION ERROR')
            results['errors'].append(f'{endpoint} (connection error)')
        except requests.exceptions.Timeout:
            print('⏱️ TIMEOUT')
            results['errors'].append(f'{endpoint} (timeout)')
        except Exception as e:
            print(f'❌ ERROR: {str(e)}')
            results['errors'].append(f'{endpoint} ({str(e)})')
    
    print('\n' + '=' * 50)
    print('📊 RESUMEN DE VERIFICACIÓN BACKEND:')
    working_count = len(results['working'])
    not_working_count = len(results['not_working'])
    errors_count = len(results['errors'])
    
    print(f'✅ Endpoints funcionando: {working_count}')
    print(f'❌ Endpoints con problemas: {not_working_count}')
    print(f'🚫 Errores de conexión: {errors_count}')
    
    if results['not_working']:
        print('\n❌ ENDPOINTS CON PROBLEMAS:')
        for endpoint in results['not_working']:
            print(f'   • {endpoint}')
    
    if results['errors']:
        print('\n🚫 ERRORES DE CONEXIÓN:')
        for error in results['errors']:
            print(f'   • {error}')
    
    if results['errors'] and any('connection error' in str(error) for error in results['errors']):
        print('\n💡 RECOMENDACIÓN: El backend parece estar apagado.')
        print('   Ejecute: python main.py')
        return False
    
    return errors_count == 0 and not_working_count == 0

def check_backend_files():
    print('\n🔍 VERIFICANDO ARCHIVOS DEL BACKEND')
    print('=' * 50)
    
    critical_files = [
        'main.py',
        'app/__init__.py',
        'app/models/__init__.py',
        'app/api/v1/__init__.py',
        'requirements.txt'
    ]
    
    missing_files = []
    for file in critical_files:
        if os.path.exists(file):
            print(f'✅ {file}')
        else:
            print(f'❌ {file} - FALTANTE')
            missing_files.append(file)
    
    return len(missing_files) == 0

def main():
    """Función principal"""
    print(f'🚀 VALIDACIÓN COMPLETA DEL BACKEND - {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print('=' * 70)
    
    # Verificar archivos críticos
    files_ok = check_backend_files()
    
    # Verificar endpoints si los archivos están bien
    if files_ok:
        endpoints_ok = test_backend_health()
    else:
        print('\n⚠️ No se puede verificar endpoints - archivos críticos faltantes')
        endpoints_ok = False
    
    # Resumen final
    print('\n' + '=' * 70)
    print('📋 RESUMEN FINAL DE VALIDACIÓN BACKEND')
    print('=' * 70)
    
    if files_ok and endpoints_ok:
        print('🎉 ¡Backend en excelente estado!')
        print('✅ Todos los archivos críticos presentes')
        print('✅ Todos los endpoints funcionando correctamente')
        status = 'EXCELLENT'
    elif files_ok and not endpoints_ok:
        print('⚠️ Backend con problemas de conectividad')
        print('✅ Archivos críticos presentes')
        print('❌ Algunos endpoints no responden')
        print('💡 Verifique que el servidor esté ejecutándose')
        status = 'NEEDS_RESTART'
    else:
        print('❌ Backend con problemas críticos')
        print('❌ Archivos críticos faltantes')
        status = 'CRITICAL'
    
    print(f'\n🎯 ESTADO: {status}')
    print('=' * 70)
    
    return files_ok and endpoints_ok

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
