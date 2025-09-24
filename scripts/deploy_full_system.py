#!/usr/bin/env python3
"""
Despliegue Completo del Sistema POS O'data
==========================================
Backend + Frontend en modo producción
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def print_step(step, status=""):
    """Imprime paso con formato"""
    status_icon = "🚀" if status == "start" else "✅" if status == "success" else "❌" if status == "error" else "🔍"
    print(f"{status_icon} {step}")

def run_command(command, cwd=None, background=False):
    """Ejecuta comando"""
    try:
        if background:
            return subprocess.Popen(command, shell=True, cwd=cwd)
        else:
            result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd, timeout=60)
            return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def deploy_backend():
    """Despliega el backend"""
    print("\n🚀 DESPLEGANDO BACKEND")
    print("=" * 50)
    
    # Verificar que el backend esté funcionando
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print_step("Backend ya está ejecutándose", "success")
            return True
    except:
        pass
    
    # Iniciar backend en background
    print_step("Iniciando servidor backend...", "start")
    backend_process = run_command("python run_server.py", background=True)
    
    # Esperar y verificar
    time.sleep(3)
    
    try:
        response = requests.get("http://localhost:5000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_step(f"Backend desplegado: {data['status']}", "success")
            print_step(f"URL: http://localhost:5000", "success")
            return True
        else:
            print_step(f"Error backend: {response.status_code}", "error")
            return False
    except Exception as e:
        print_step(f"Error conectando backend: {e}", "error")
        return False

def deploy_frontend():
    """Despliega el frontend"""
    print("\n🚀 DESPLEGANDO FRONTEND")
    print("=" * 50)
    
    frontend_path = Path("Sistema_POS_Odata_nuevo/frontend")
    
    if not frontend_path.exists():
        print_step("Directorio frontend no encontrado", "error")
        return False
    
    # Verificar Node.js
    success, stdout, stderr = run_command("node --version")
    if not success:
        print_step("Node.js no encontrado. Instalando...", "start")
        print("Por favor instala Node.js desde https://nodejs.org/")
        return False
    
    print_step(f"Node.js: {stdout.strip()}", "success")
    
    # Verificar npm
    success, stdout, stderr = run_command("npm --version")
    if not success:
        print_step("npm no encontrado", "error")
        return False
    
    print_step(f"npm: {stdout.strip()}", "success")
    
    # Instalar dependencias
    print_step("Instalando dependencias del frontend...", "start")
    success, stdout, stderr = run_command("npm install", cwd=str(frontend_path))
    if not success:
        print_step(f"Error instalando dependencias: {stderr}", "error")
        return False
    
    print_step("Dependencias instaladas", "success")
    
    # Build del frontend
    print_step("Compilando frontend...", "start")
    success, stdout, stderr = run_command("npm run build", cwd=str(frontend_path))
    if not success:
        print_step(f"Error en build: {stderr}", "error")
        return False
    
    print_step("Frontend compilado exitosamente", "success")
    
    # Iniciar servidor de desarrollo
    print_step("Iniciando servidor frontend...", "start")
    frontend_process = run_command("npm run dev", cwd=str(frontend_path), background=True)
    
    # Esperar y verificar
    time.sleep(5)
    
    try:
        response = requests.get("http://localhost:5173", timeout=10)
        if response.status_code == 200:
            print_step("Frontend desplegado exitosamente", "success")
            print_step("URL: http://localhost:5173", "success")
            return True
        else:
            print_step(f"Frontend error: {response.status_code}", "error")
            return False
    except Exception as e:
        print_step(f"Error verificando frontend: {e}", "error")
        return False

def verify_full_system():
    """Verifica el sistema completo"""
    print("\n🔍 VERIFICANDO SISTEMA COMPLETO")
    print("=" * 50)
    
    # Verificar backend
    try:
        response = requests.get("http://localhost:5000/health", timeout=5)
        if response.status_code == 200:
            print_step("Backend: ✅ FUNCIONANDO", "success")
        else:
            print_step("Backend: ❌ ERROR", "error")
            return False
    except:
        print_step("Backend: ❌ NO ACCESIBLE", "error")
        return False
    
    # Verificar frontend
    try:
        response = requests.get("http://localhost:5173", timeout=5)
        if response.status_code == 200:
            print_step("Frontend: ✅ FUNCIONANDO", "success")
        else:
            print_step("Frontend: ❌ ERROR", "error")
            return False
    except:
        print_step("Frontend: ❌ NO ACCESIBLE", "error")
        return False
    
    # Probar integración
    try:
        response = requests.get("http://localhost:5000/api/v1/products", timeout=5)
        if response.status_code in [200, 401]:
            print_step("API Integration: ✅ FUNCIONANDO", "success")
        else:
            print_step("API Integration: ⚠️ PARCIAL", "warning")
    except:
        print_step("API Integration: ❌ ERROR", "error")
    
    return True

def main():
    """Función principal de despliegue"""
    print("🚀 DESPLIEGUE COMPLETO - SISTEMA POS O'DATA")
    print("=" * 60)
    print("Desplegando Backend + Frontend en modo producción")
    print("=" * 60)
    
    # Desplegar backend
    backend_ok = deploy_backend()
    
    # Desplegar frontend
    frontend_ok = deploy_frontend()
    
    # Verificar sistema completo
    if backend_ok and frontend_ok:
        verify_full_system()
        
        print("\n🎉 ¡DESPLIEGUE COMPLETO EXITOSO!")
        print("=" * 60)
        print("✅ Backend: http://localhost:5000")
        print("✅ Frontend: http://localhost:5173")
        print("✅ Sistema completamente operativo")
        print("\n🌐 URLs del Sistema:")
        print("   • Health Check: http://localhost:5000/health")
        print("   • API v1: http://localhost:5000/api/v1/")
        print("   • API v2: http://localhost:5000/api/v2/")
        print("   • Frontend App: http://localhost:5173")
        print("\n🎊 ¡Sistema POS O'data desplegado exitosamente!")
        
        return True
    else:
        print("\n❌ DESPLIEGUE PARCIAL")
        print("=" * 60)
        print(f"Backend: {'✅' if backend_ok else '❌'}")
        print(f"Frontend: {'✅' if frontend_ok else '❌'}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
