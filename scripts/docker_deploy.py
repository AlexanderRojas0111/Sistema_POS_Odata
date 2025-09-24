#!/usr/bin/env python3
"""
Despliegue con Docker - Sistema POS O'data
==========================================
Despliegue profesional usando Docker y Docker Compose
"""

import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def print_step(step, status=""):
    """Imprime paso con formato"""
    status_icon = "🐳" if status == "docker" else "✅" if status == "success" else "❌" if status == "error" else "🔍"
    print(f"{status_icon} {step}")

def run_command(command, cwd=None):
    """Ejecuta comando"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd, timeout=120)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_docker():
    """Verifica que Docker esté instalado"""
    print("\n🐳 VERIFICANDO DOCKER")
    print("-" * 40)
    
    success, stdout, stderr = run_command("docker --version")
    if success:
        print_step(f"Docker: {stdout.strip()}", "success")
        return True
    else:
        print_step("Docker no encontrado", "error")
        print("Instala Docker desde: https://www.docker.com/get-started/")
        return False

def check_docker_compose():
    """Verifica Docker Compose"""
    print("\n🐳 VERIFICANDO DOCKER COMPOSE")
    print("-" * 40)
    
    success, stdout, stderr = run_command("docker-compose --version")
    if success:
        print_step(f"Docker Compose: {stdout.strip()}", "success")
        return True
    else:
        print_step("Docker Compose no encontrado", "error")
        return False

def build_containers():
    """Construye los contenedores"""
    print("\n🐳 CONSTRUYENDO CONTENEDORES")
    print("-" * 40)
    
    # Construir backend
    print_step("Construyendo backend...", "docker")
    success, stdout, stderr = run_command("docker build -t pos-odata-backend .")
    if success:
        print_step("Backend construido exitosamente", "success")
    else:
        print_step(f"Error construyendo backend: {stderr}", "error")
        return False
    
    return True

def start_services():
    """Inicia los servicios con Docker Compose"""
    print("\n🐳 INICIANDO SERVICIOS")
    print("-" * 40)
    
    # Verificar que existe docker-compose.yml
    if not Path("docker-compose.yml").exists():
        print_step("docker-compose.yml no encontrado", "error")
        return False
    
    # Iniciar servicios
    print_step("Iniciando servicios con Docker Compose...", "docker")
    success, stdout, stderr = run_command("docker-compose up -d")
    if success:
        print_step("Servicios iniciados exitosamente", "success")
        return True
    else:
        print_step(f"Error iniciando servicios: {stderr}", "error")
        return False

def verify_deployment():
    """Verifica el despliegue"""
    print("\n🔍 VERIFICANDO DESPLIEGUE")
    print("-" * 40)
    
    # Esperar que los servicios estén listos
    print_step("Esperando que los servicios estén listos...", "docker")
    time.sleep(10)
    
    # Verificar backend
    try:
        response = requests.get("http://localhost:5000/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print_step(f"Backend: {data['status']}", "success")
        else:
            print_step(f"Backend error: {response.status_code}", "error")
            return False
    except Exception as e:
        print_step(f"Backend no accesible: {e}", "error")
        return False
    
    # Verificar frontend
    try:
        response = requests.get("http://localhost:5173", timeout=10)
        if response.status_code == 200:
            print_step("Frontend: Funcionando", "success")
        else:
            print_step(f"Frontend error: {response.status_code}", "error")
    except Exception as e:
        print_step(f"Frontend no accesible: {e}", "error")
    
    return True

def show_status():
    """Muestra estado de los contenedores"""
    print("\n📊 ESTADO DE CONTENEDORES")
    print("-" * 40)
    
    success, stdout, stderr = run_command("docker-compose ps")
    if success:
        print(stdout)
    else:
        print_step("Error obteniendo estado", "error")

def main():
    """Función principal de despliegue con Docker"""
    print("🐳 DESPLIEGUE CON DOCKER - SISTEMA POS O'DATA")
    print("=" * 60)
    print("Desplegando Backend + Frontend + Redis con Docker")
    print("=" * 60)
    
    # Verificar Docker
    if not check_docker():
        return False
    
    if not check_docker_compose():
        return False
    
    # Construir contenedores
    if not build_containers():
        return False
    
    # Iniciar servicios
    if not start_services():
        return False
    
    # Verificar despliegue
    if not verify_deployment():
        return False
    
    # Mostrar estado
    show_status()
    
    print("\n🎉 ¡DESPLIEGUE CON DOCKER EXITOSO!")
    print("=" * 60)
    print("✅ Backend: http://localhost:5000")
    print("✅ Frontend: http://localhost:5173")
    print("✅ Redis: localhost:6379")
    print("\n🌐 URLs del Sistema:")
    print("   • Health Check: http://localhost:5000/health")
    print("   • API v1: http://localhost:5000/api/v1/")
    print("   • Frontend App: http://localhost:5173")
    print("\n🎊 ¡Sistema POS O'data desplegado con Docker!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
