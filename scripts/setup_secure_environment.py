#!/usr/bin/env python3
"""
Script de configuración segura del entorno
Sistema POS O'Data v2.0.0
"""

import os
import secrets
import string
import shutil
from pathlib import Path

def generate_secure_password(length=32):
    """Generar contraseña segura"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_secret_key(length=32):
    """Generar clave secreta segura"""
    return secrets.token_urlsafe(length)

def create_secure_env_file():
    """Crear archivo .env con valores seguros"""
    
    # Generar valores seguros
    secret_key = generate_secret_key(32)
    jwt_secret = generate_secret_key(32)
    redis_password = generate_secure_password(24)
    postgres_password = generate_secure_password(24)
    grafana_password = generate_secure_password(16)
    
    # Plantilla del archivo .env
    env_content = f"""# ==============================================
# CONFIGURACIÓN SEGURA - Sistema POS O'Data v2.0.0
# ==============================================
# ⚠️ IMPORTANTE: Este archivo contiene información sensible
# 🔒 NO commitear este archivo al repositorio

# ===== APLICACIÓN PRINCIPAL =====
FLASK_ENV=production
SECRET_KEY={secret_key}
JWT_SECRET_KEY={jwt_secret}
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=WARNING

# ===== BASE DE DATOS =====
DATABASE_URL=sqlite:///instance/pos_odata.db
POSTGRES_DB=pos_odata
POSTGRES_USER=pos_user
POSTGRES_PASSWORD={postgres_password}

# ===== REDIS CACHE =====
REDIS_PASSWORD={redis_password}
REDIS_URL=redis://:{redis_password}@redis:6379/0
RATELIMIT_STORAGE_URL=redis://:{redis_password}@redis:6379/1

# ===== MONITOREO =====
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD={grafana_password}
PROMETHEUS_RETENTION_TIME=30d

# ===== ALERTAS =====
ALERT_EMAIL=admin@your-domain.com
SMTP_SERVER=smtp.your-domain.com
SMTP_PORT=587
SMTP_USER=alerts@your-domain.com
SMTP_PASSWORD=change-this-smtp-password

# ===== EMPRESA =====
COMPANY_NAME="Su Empresa"
COMPANY_EMAIL=info@your-domain.com
COMPANY_PHONE="+57 300 123 4567"

# ===== DESARROLLO =====
DEBUG=false
TESTING=false
DEVELOPMENT_MODE=false

# ===== NOTAS =====
# Generado automáticamente el {os.popen('date').read().strip()}
# Para regenerar: python scripts/setup_secure_environment.py
"""

    # Escribir archivo .env
    with open('.env', 'w') as f:
        f.write(env_content)
    
    # Establecer permisos seguros
    os.chmod('.env', 0o600)
    
    return {
        'secret_key': secret_key,
        'jwt_secret': jwt_secret,
        'redis_password': redis_password,
        'postgres_password': postgres_password,
        'grafana_password': grafana_password
    }

def create_gitignore_entry():
    """Asegurar que .env está en .gitignore"""
    gitignore_path = '.gitignore'
    
    # Leer .gitignore existente
    gitignore_content = ""
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as f:
            gitignore_content = f.read()
    
    # Añadir entrada si no existe
    env_entries = ['.env', '.env.local', '.env.production', '.env.staging']
    
    for entry in env_entries:
        if entry not in gitignore_content:
            gitignore_content += f"\n{entry}"
    
    # Escribir .gitignore actualizado
    with open(gitignore_path, 'w') as f:
        f.write(gitignore_content.strip() + '\n')

def create_credentials_file(credentials):
    """Crear archivo de credenciales para referencia segura"""
    
    credentials_content = f"""# ==============================================
# CREDENCIALES DEL SISTEMA - Sistema POS O'Data v2.0.0
# ==============================================
# ⚠️ GUARDAR EN LUGAR SEGURO - NO COMPARTIR
# 🔒 ELIMINAR DESPUÉS DE CONFIGURAR PRODUCCIÓN

Aplicación:
  Secret Key: {credentials['secret_key'][:20]}...
  JWT Secret: {credentials['jwt_secret'][:20]}...

Base de Datos:
  PostgreSQL Password: {credentials['postgres_password']}

Cache:
  Redis Password: {credentials['redis_password']}

Monitoreo:
  Grafana Admin: admin
  Grafana Password: {credentials['grafana_password']}

URLs de Acceso (después del despliegue):
  Aplicación: http://localhost:8000
  Grafana: http://localhost:3000
  Prometheus: http://localhost:9090

Notas de Seguridad:
1. Cambiar contraseñas SMTP y de empresa
2. Configurar SSL/TLS en producción
3. Usar gestor de secretos para producción enterprise
4. Eliminar este archivo después de la configuración

Generado: {os.popen('date').read().strip()}
"""

    # Crear directorio seguro
    secure_dir = Path('secure')
    secure_dir.mkdir(exist_ok=True)
    
    # Escribir archivo de credenciales
    credentials_file = secure_dir / 'credentials.txt'
    with open(credentials_file, 'w') as f:
        f.write(credentials_content)
    
    # Establecer permisos muy restrictivos
    os.chmod(credentials_file, 0o600)
    os.chmod(secure_dir, 0o700)

def validate_environment():
    """Validar que el entorno está configurado correctamente"""
    
    print("🔍 Validando configuración del entorno...")
    
    # Verificar archivos críticos
    required_files = ['.env', 'env.example', '.gitignore']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Archivos faltantes: {', '.join(missing_files)}")
        return False
    
    # Verificar permisos de .env
    env_stat = os.stat('.env')
    if oct(env_stat.st_mode)[-3:] != '600':
        print("⚠️ Permisos de .env no son seguros (debería ser 600)")
    
    # Verificar que .env no está en git
    if os.path.exists('.git'):
        git_status = os.popen('git status --porcelain .env 2>/dev/null').read()
        if git_status.strip():
            print("⚠️ ADVERTENCIA: .env podría estar trackeado por Git")
    
    print("✅ Configuración del entorno validada")
    return True

def main():
    """Función principal"""
    print("🚀 Configurando entorno seguro para Sistema POS O'Data v2.0.0")
    print("="*60)
    
    try:
        # Crear archivo .env seguro
        print("🔐 Generando archivo .env con credenciales seguras...")
        credentials = create_secure_env_file()
        print("✅ Archivo .env creado con éxito")
        
        # Actualizar .gitignore
        print("📝 Actualizando .gitignore...")
        create_gitignore_entry()
        print("✅ .gitignore actualizado")
        
        # Crear archivo de credenciales
        print("📋 Creando archivo de credenciales de referencia...")
        create_credentials_file(credentials)
        print("✅ Credenciales guardadas en secure/credentials.txt")
        
        # Validar configuración
        if validate_environment():
            print("\n🎉 ¡Configuración segura completada con éxito!")
            print("\n📋 PRÓXIMOS PASOS:")
            print("1. Revisar y personalizar valores en .env")
            print("2. Configurar SMTP y datos de empresa")
            print("3. Ejecutar: docker-compose up -d")
            print("4. Verificar: python scripts/yaml_deep_validator.py")
            print("5. Eliminar secure/credentials.txt después de configurar")
            print("\n🔒 IMPORTANTE:")
            print("• NUNCA commitear el archivo .env")
            print("• Usar gestores de secretos en producción")
            print("• Rotar credenciales regularmente")
        else:
            print("❌ Error en la validación del entorno")
            return 1
            
    except Exception as e:
        print(f"❌ Error durante la configuración: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
