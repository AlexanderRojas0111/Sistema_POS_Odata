#!/usr/bin/env python3
"""
Script para configurar un archivo .env seguro
============================================

Genera un archivo .env con claves secretas seguras y configuración apropiada
para desarrollo y producción.

Versión: 2.0.0
"""

import os
import secrets
from pathlib import Path

def generate_secure_keys():
    """Genera claves secretas seguras"""
    return {
        'SECRET_KEY': secrets.token_urlsafe(64),
        'JWT_SECRET_KEY': secrets.token_urlsafe(64),
        'CSRF_SECRET_KEY': secrets.token_urlsafe(32)
    }

def create_secure_env_file(environment='development'):
    """Crea un archivo .env seguro"""
    
    project_root = Path(__file__).parent.parent
    env_file = project_root / '.env'
    
    keys = generate_secure_keys()
    
    if environment == 'development':
        content = f"""# ========================================================================
# Sistema POS O'data - Variables de Entorno (DESARROLLO)
# ========================================================================
# IMPORTANTE: Este archivo contiene configuración para DESARROLLO únicamente
# Para PRODUCCIÓN, usar claves seguras generadas automáticamente
# ========================================================================

# ========================================================================
# CONFIGURACIÓN BÁSICA
# ========================================================================
FLASK_ENV=development
SECRET_KEY={keys['SECRET_KEY']}
JWT_SECRET_KEY={keys['JWT_SECRET_KEY']}

# ========================================================================
# BASE DE DATOS
# ========================================================================
# Desarrollo (SQLite)
DATABASE_URL=sqlite:///pos_odata_dev.db

# ========================================================================
# REDIS Y CACHE
# ========================================================================
REDIS_URL=redis://localhost:6379/0
RATELIMIT_ENABLED=false

# ========================================================================
# CORS Y SEGURIDAD
# ========================================================================
# Desarrollo - Dominios específicos (NO usar *)
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,http://localhost:5000

# ========================================================================
# LOGGING Y MONITOREO
# ========================================================================
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# ========================================================================
# CONFIGURACIÓN DE DESARROLLO
# ========================================================================
DEBUG=true
TESTING=false
"""
    
    elif environment == 'production':
        content = f"""# ========================================================================
# Sistema POS O'data - Variables de Entorno (PRODUCCIÓN)
# ========================================================================
# IMPORTANTE: Configuración para PRODUCCIÓN - Mantener seguro
# ========================================================================

# ========================================================================
# CONFIGURACIÓN BÁSICA
# ========================================================================
FLASK_ENV=production
SECRET_KEY={keys['SECRET_KEY']}
JWT_SECRET_KEY={keys['JWT_SECRET_KEY']}

# ========================================================================
# BASE DE DATOS
# ========================================================================
# Producción (PostgreSQL) - CAMBIAR con tus credenciales reales
DATABASE_URL=postgresql://pos_user:secure_password_here@localhost:5432/pos_odata_prod

# ========================================================================
# REDIS Y CACHE
# ========================================================================
REDIS_URL=redis://localhost:6379/0
RATELIMIT_ENABLED=true

# ========================================================================
# CORS Y SEGURIDAD
# ========================================================================
# Producción - CAMBIAR con tu dominio real
CORS_ORIGINS=https://tu-dominio.com

# ========================================================================
# LOGGING Y MONITOREO
# ========================================================================
LOG_LEVEL=WARNING
LOG_FILE=logs/app.log

# ========================================================================
# CONFIGURACIÓN DE PRODUCCIÓN
# ========================================================================
DEBUG=false
TESTING=false
"""
    
    # Escribir archivo
    with open(env_file, 'w') as f:
        f.write(content)
    
    print(f"✅ Archivo .env creado para {environment}")
    print(f"📁 Ubicación: {env_file}")
    print(f"🔑 Claves seguras generadas automáticamente")
    
    if environment == 'production':
        print("\n⚠️  IMPORTANTE para PRODUCCIÓN:")
        print("   1. Cambiar DATABASE_URL con credenciales reales")
        print("   2. Cambiar CORS_ORIGINS con tu dominio real")
        print("   3. Configurar Redis si usas un servidor externo")
        print("   4. Revisar todas las configuraciones antes del despliegue")

def main():
    """Función principal"""
    import sys
    
    if len(sys.argv) > 1:
        environment = sys.argv[1].lower()
        if environment not in ['development', 'production']:
            print("❌ Entorno debe ser 'development' o 'production'")
            sys.exit(1)
    else:
        environment = 'development'
    
    create_secure_env_file(environment)
    
    print(f"\n🔒 Configuración de seguridad aplicada para {environment}")
    print("🎯 Próximos pasos:")
    print("   1. Verificar configuraciones en .env")
    print("   2. Ejecutar: python scripts/security_audit.py")
    print("   3. Iniciar servidor: python run_server.py")

if __name__ == "__main__":
    main()
