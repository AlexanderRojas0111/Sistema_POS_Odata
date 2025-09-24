#!/usr/bin/env python3
"""
Despliegue Rápido con Docker - Sistema POS O'data
=================================================
Versión simplificada para evitar problemas de codificación
"""

import os
import sys
import subprocess
import time
import requests

def print_step(step, status=""):
    """Imprime paso con formato"""
    status_icon = "🐳" if status == "docker" else "✅" if status == "success" else "❌" if status == "error" else "🔍"
    print(f"{status_icon} {step}")

def run_command_simple(command):
    """Ejecuta comando de forma simple"""
    try:
        result = subprocess.run(command, shell=True, timeout=60)
        return result.returncode == 0
    except:
        return False

def deploy_with_docker():
    """Despliegue simplificado con Docker"""
    print("\n🐳 DESPLIEGUE RÁPIDO CON DOCKER")
    print("=" * 50)
    
    # 1. Detener servicios existentes
    print_step("Deteniendo servicios existentes...", "docker")
    run_command_simple("docker-compose down")
    
    # 2. Iniciar solo backend con Docker
    print_step("Iniciando backend con Docker...", "docker")
    backend_ok = run_command_simple("docker run -d --name pos-backend -p 5000:5000 -v ${PWD}:/app -w /app python:3.13-slim python run_server.py")
    
    if backend_ok:
        print_step("Backend iniciado con Docker", "success")
    else:
        print_step("Error iniciando backend", "error")
        return False
    
    # 3. Iniciar frontend con Node.js Docker
    print_step("Iniciando frontend con Node.js Docker...", "docker")
    frontend_ok = run_command_simple("docker run -d --name pos-frontend -p 5173:5173 -v ${PWD}/Sistema_POS_Odata_nuevo/frontend:/app -w /app node:22-alpine sh -c 'npm install && npm run dev -- --host 0.0.0.0 --port 5173'")
    
    if frontend_ok:
        print_step("Frontend iniciado con Docker", "success")
    else:
        print_step("Error iniciando frontend", "error")
    
    # 4. Verificar despliegue
    print_step("Verificando despliegue...", "docker")
    time.sleep(5)
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=10)
        if response.status_code == 200:
            print_step("Backend funcionando", "success")
            return True
        else:
            print_step("Backend error", "error")
            return False
    except:
        print_step("Backend no accesible", "error")
        return False

def main():
    """Función principal"""
    print("🚀 DESPLIEGUE RÁPIDO - SISTEMA POS O'DATA")
    print("=" * 60)
    
    success = deploy_with_docker()
    
    if success:
        print("\n🎉 ¡DESPLIEGUE EXITOSO!")
        print("✅ Backend: http://localhost:5000")
        print("✅ Frontend: http://localhost:5173")
        print("\n🌐 URLs del Sistema:")
        print("   • Health Check: http://localhost:5000/health")
        print("   • API v1: http://localhost:5000/api/v1/")
        print("   • Frontend App: http://localhost:5173")
    else:
        print("\n❌ Error en despliegue")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
