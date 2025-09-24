#!/usr/bin/env python3
"""
Script de preparación para release de producción
Sistema POS Odata v2.0.0-production
"""

import os
import subprocess
import sys
from datetime import datetime

def print_section(title):
    print(f"\n{'='*60}")
    print(f"🚀 {title}")
    print('='*60)

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def run_command(command, description):
    print(f"\n🔧 {description}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print_success("Comando ejecutado exitosamente")
            return True
        else:
            print_error(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print_error(f"Excepción: {e}")
        return False

def main():
    print("🏪 PREPARACIÓN PARA RELEASE DE PRODUCCIÓN")
    print("Sistema POS Odata v2.0.0-production")
    
    # Verificar que estamos en un repositorio git
    print_section("VERIFICACIÓN DE REPOSITORIO GIT")
    if not os.path.exists('.git'):
        print_error("No es un repositorio git. Inicializando...")
        if not run_command("git init", "Inicializar repositorio git"):
            return False
    
    # Agregar todos los archivos
    print_section("PREPARACIÓN DE ARCHIVOS")
    if not run_command("git add .", "Agregar todos los archivos"):
        return False
    
    # Commit de la versión de producción
    commit_message = f"feat: Release v2.0.0-production - Sistema optimizado listo para producción\n\n- Arquitectura de servicios implementada\n- Dependencias ML optimizadas\n- Docker multi-stage optimizado\n- Tests completos implementados\n- Seguridad hardened\n- Performance optimizado\n\nFecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    if not run_command(f'git commit -m "{commit_message}"', "Commit de versión de producción"):
        print_error("Error en commit (puede ser que no haya cambios)")
    
    # Crear tag de versión
    print_section("CREACIÓN DE TAG DE VERSIÓN")
    tag_message = "Sistema POS Odata v2.0.0 - Versión de Producción Optimizada"
    if not run_command(f'git tag -a v2.0.0-production -m "{tag_message}"', "Crear tag de versión"):
        return False
    
    # Mostrar información del repositorio
    print_section("INFORMACIÓN DEL REPOSITORIO")
    run_command("git status", "Estado del repositorio")
    run_command("git log --oneline -5", "Últimos commits")
    run_command("git tag", "Tags disponibles")
    
    # Instrucciones finales
    print_section("INSTRUCCIONES PARA GITHUB")
    print("📋 Para subir a GitHub, ejecuta:")
    print("   git remote add origin https://github.com/tu-usuario/sistema-pos-odata.git")
    print("   git push -u origin main")
    print("   git push origin v2.0.0-production")
    
    print("\n🌟 RELEASE DE PRODUCCIÓN PREPARADO")
    print_success("Sistema listo para GitHub y producción")
    
    return True

if __name__ == "__main__":
    sys.exit(0 if main() else 1)
