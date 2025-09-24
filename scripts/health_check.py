#!/usr/bin/env python3
"""
Script de verificación de salud del Sistema POS O'data
"""

import requests
import json
import sys
import os
from datetime import datetime

# Configuración
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:5000')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

def check_backend():
    """Verificar estado del backend"""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            return True, "Backend OK"
        else:
            return False, f"Backend HTTP {response.status_code}"
    except Exception as e:
        return False, f"Backend Error: {str(e)}"

def check_frontend():
    """Verificar estado del frontend"""
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            return True, "Frontend OK"
        else:
            return False, f"Frontend HTTP {response.status_code}"
    except Exception as e:
        return False, f"Frontend Error: {str(e)}"

def main():
    """Función principal"""
    print("🔍 Verificando salud del Sistema POS O'data...")
    
    backend_ok, backend_msg = check_backend()
    frontend_ok, frontend_msg = check_frontend()
    
    print(f"Backend: {'✅' if backend_ok else '❌'} {backend_msg}")
    print(f"Frontend: {'✅' if frontend_ok else '❌'} {frontend_msg}")
    
    if backend_ok and frontend_ok:
        print("🎉 Sistema completamente funcional!")
        sys.exit(0)
    else:
        print("⚠️ Sistema con problemas")
        sys.exit(1)

if __name__ == '__main__':
    main() 