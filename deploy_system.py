#!/usr/bin/env python3
"""
Script completo de despliegue del Sistema POS Odata
Ejecuta todas las validaciones y despliega el sistema completo
"""

import os
import sys
import subprocess
import time
import threading
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_command(command, cwd=None):
    """Ejecutar comando y retornar resultado"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=cwd)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def validate_system():
    """Validar que el sistema esté listo para despliegue"""
    print("🔍 VALIDANDO SISTEMA")
    print("-" * 30)
    
    # Validar entorno virtual
    if 'venv_pos_clean' not in sys.executable:
        print("⚠️  Recomendación: Activar entorno virtual venv_pos_clean")
    else:
        print("✅ Entorno virtual activado")
    
    # Validar dependencias Python
    success, _, _ = run_command("python -c \"import flask, sqlalchemy, redis; print('Dependencias OK')\"")
    if success:
        print("✅ Dependencias Python instaladas")
    else:
        print("❌ Error con dependencias Python")
        return False
    
    # Validar aplicación
    success, _, _ = run_command("python test_app.py")
    if success:
        print("✅ Aplicación validada correctamente")
    else:
        print("❌ Error validando aplicación")
        return False
    
    # Validar frontend
    if os.path.exists("frontend/node_modules"):
        print("✅ Dependencias frontend instaladas")
    else:
        print("⚠️  Dependencias frontend no encontradas")
    
    return True

def start_backend():
    """Iniciar servidor backend"""
    print("\n🚀 INICIANDO BACKEND")
    print("-" * 30)
    
    # Ejecutar servidor
    os.system("python run_server.py")

def start_frontend():
    """Iniciar servidor frontend"""
    print("\n🌐 INICIANDO FRONTEND")
    print("-" * 30)
    
    success, output, error = run_command("npm start", cwd="frontend")
    if not success:
        print(f"❌ Error iniciando frontend: {error}")
    else:
        print("✅ Frontend iniciado")

def deploy_complete_system():
    """Desplegar sistema completo"""
    print("🎯 DESPLEGANDO SISTEMA COMPLETO POS ODATA")
    print("=" * 60)
    
    # Validar sistema
    if not validate_system():
        print("❌ Sistema no válido para despliegue")
        return False
    
    print("\n✅ SISTEMA VALIDADO CORRECTAMENTE")
    print("=" * 60)
    
    # Mostrar información del despliegue
    print("\n📋 INFORMACIÓN DEL DESPLIEGUE:")
    print("-" * 40)
    print("🔧 Backend: http://localhost:5000")
    print("🌐 Frontend: http://localhost:3000")
    print("📊 Health Check: http://localhost:5000/health")
    print("🔍 API: http://localhost:5000/api/v1/")
    print("📄 Base de datos: SQLite (pos_odata_dev.db)")
    print("💾 Cache: MockRedis (en memoria)")
    print("🔐 Seguridad: Básica (desarrollo)")
    
    print("\n🎉 SISTEMA LISTO PARA USO")
    print("=" * 60)
    
    # Preguntar si iniciar servidores
    response = input("\n¿Desea iniciar el servidor backend ahora? (y/n): ").lower()
    if response == 'y':
        print("\n🚀 Iniciando servidor backend...")
        print("💡 Tip: Abra otra terminal y ejecute 'cd frontend && npm start' para el frontend")
        start_backend()
    else:
        print("\n📝 Para iniciar manualmente:")
        print("   Backend: python run_server.py")
        print("   Frontend: cd frontend && npm start")
    
    return True

def main():
    """Función principal"""
    try:
        success = deploy_complete_system()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n🛑 Despliegue cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error durante el despliegue: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
