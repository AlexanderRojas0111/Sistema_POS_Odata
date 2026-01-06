#!/usr/bin/env python3
"""
Script de Validación de Endpoints
Sistema POS O'Data v2.0.2-enterprise
====================================
Valida que los endpoints principales de la API funcionen correctamente.
"""

import sys
import requests
import json
from pathlib import Path
from typing import Dict, List, Tuple

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

BASE_URL = "http://localhost:8000"

def test_endpoint(method: str, endpoint: str, data: dict = None, headers: dict = None, expected_status: int = 200) -> Tuple[bool, str]:
    """Probar un endpoint"""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == 'GET':
            response = requests.get(url, headers=headers, timeout=10)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers=headers, timeout=10)
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers=headers, timeout=10)
        elif method.upper() == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=10)
        else:
            return False, f"Método {method} no soportado"
        
        if response.status_code == expected_status:
            return True, f"✅ {method} {endpoint} - Status: {response.status_code}"
        else:
            return False, f"❌ {method} {endpoint} - Status: {response.status_code} (esperado: {expected_status})"
            
    except requests.exceptions.ConnectionError:
        return False, f"❌ {method} {endpoint} - Error de conexión"
    except requests.exceptions.Timeout:
        return False, f"❌ {method} {endpoint} - Timeout"
    except Exception as e:
        return False, f"❌ {method} {endpoint} - Error: {str(e)}"

def validate_endpoints():
    """Validar endpoints principales"""
    print("=" * 60)
    print("VALIDACIÓN DE ENDPOINTS")
    print("Sistema POS O'Data v2.0.2-enterprise")
    print("=" * 60)
    print()
    
    results: List[Tuple[bool, str]] = []
    
    # Endpoints públicos (sin autenticación)
    print("📋 Endpoints Públicos:")
    print("-" * 60)
    
    public_endpoints = [
        ('GET', '/api/v1/health'),
        ('GET', '/api/v1/health/detailed'),
        ('GET', '/api/v1/health/metrics'),
    ]
    
    for method, endpoint in public_endpoints:
        result = test_endpoint(method, endpoint)
        results.append(result)
        print(result[1])
    
    print()
    
    # Endpoints de autenticación
    print("🔐 Endpoints de Autenticación:")
    print("-" * 60)
    
    # Probar login (puede fallar si no hay credenciales válidas, pero debe responder)
    login_result = test_endpoint('POST', '/api/v1/auth/login', 
                                data={'username': 'admin', 'password': 'admin123'},
                                expected_status=200)  # Puede ser 200 o 401
    results.append(login_result)
    print(login_result[1])
    
    print()
    
    # Resumen
    print("=" * 60)
    print("RESUMEN")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for success, _ in results if success)
    failed = total - passed
    
    print(f"Total de endpoints probados: {total}")
    print(f"✅ Exitosos: {passed}")
    print(f"❌ Fallidos: {failed}")
    print()
    
    if failed > 0:
        print("Endpoints con problemas:")
        for success, message in results:
            if not success:
                print(f"  {message}")
    
    return failed == 0

if __name__ == '__main__':
    success = validate_endpoints()
    
    if success:
        print("\n✅ Todos los endpoints validados correctamente")
        sys.exit(0)
    else:
        print("\n⚠️  Algunos endpoints tienen problemas")
        sys.exit(1)
