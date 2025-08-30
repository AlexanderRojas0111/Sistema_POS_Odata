#!/usr/bin/env python3
"""
Servidor POS O'data en puerto 8000
Configurado para desarrollo con todas las funcionalidades
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def check_redis_availability():
    """Verifica la disponibilidad de Redis"""
    try:
        import redis
        r = redis.from_url('redis://localhost:6379/0')
        r.ping()
        logger.info("✅ Redis disponible y conectado")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Redis no disponible: {e}")
        logger.info("ℹ️ El sistema continuará en modo sin caché")
        return False

def check_critical_dependencies():
    """Verifica dependencias críticas del sistema"""
    dependencies = {
        'flask': 'Flask Framework',
        'sklearn': 'scikit-learn (Machine Learning)',
        'sqlalchemy': 'SQLAlchemy (ORM)',
        'jwt': 'PyJWT (Autenticación)',
        'marshmallow': 'Marshmallow (Validación)',
        'pydantic': 'Pydantic (Validación de tipos)'
    }
    
    missing_deps = []
    available_deps = []
    
    for module, description in dependencies.items():
        try:
            __import__(module)
            available_deps.append(f"✅ {description}")
        except ImportError:
            missing_deps.append(f"❌ {description}")
    
    # Mostrar estado de dependencias
    logger.info("📦 DEPENDENCIAS CRÍTICAS:")
    for dep in available_deps:
        logger.info(f"   {dep}")
    
    if missing_deps:
        logger.warning("⚠️ DEPENDENCIAS FALTANTES:")
        for dep in missing_deps:
            logger.warning(f"   {dep}")
        logger.warning("💡 Instala las dependencias faltantes con: pip install -r requirements.txt")
        return False
    
    return True

def main():
    """Función principal del servidor"""
    try:
        # Verificar que estamos en el directorio correcto
        if not Path('app').exists():
            logger.error("Directorio 'app' no encontrado. Ejecuta desde la raíz del proyecto.")
            sys.exit(1)
        
        # Verificar dependencias críticas
        logger.info("🔍 Verificando dependencias del sistema...")
        
        # Verificar dependencias críticas
        if not check_critical_dependencies():
            logger.error("❌ Faltan dependencias críticas. No se puede continuar.")
            sys.exit(1)
        
        # Verificar Redis
        redis_available = check_redis_availability()
        
        # Importar la aplicación
        from app import create_app
        
        # Crear la aplicación Flask
        app = create_app('development')
        
        # Configuración del servidor - PUERTO 8000 como solicitado
        host = os.environ.get('FLASK_HOST', '127.0.0.1')
        port = int(os.environ.get('FLASK_PORT', 8000))  # Puerto 8000 por defecto
        debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
        
        logger.info("🚀 INICIANDO SERVIDOR POS ODATA EN PUERTO 8000")
        logger.info("=" * 60)
        logger.info(f"🌐 Host: {host}")
        logger.info(f"🔌 Puerto: {port}")
        logger.info(f"🐛 Debug: {debug}")
        logger.info(f"📁 Directorio: {os.getcwd()}")
        logger.info("=" * 60)
        logger.info("🎯 RUTAS DISPONIBLES:")
        logger.info("   📦 /api/v1/productos/     - Gestión de productos")
        logger.info("   💰 /api/v1/ventas/        - Gestión de ventas")
        logger.info("   👥 /api/v1/usuarios/      - Gestión de usuarios")
        logger.info("   🤖 /api/v2/ai/            - Funcionalidades de IA")
        logger.info("   📊 /health                - Estado del sistema")
        logger.info("=" * 60)
        logger.info("✅ Servidor listo - Presiona Ctrl+C para detener")
        logger.info("🚀 Iniciando servidor Flask...")
        
        # Mostrar estado del sistema
        logger.info("📊 ESTADO DEL SISTEMA:")
        logger.info(f"   🔴 Redis: {'Disponible' if redis_available else 'No disponible (modo sin caché)'}")
        logger.info(f"   🗄️ Base de datos: SQLite (desarrollo)")
        logger.info(f"   🤖 IA: scikit-learn + TF-IDF")
        logger.info(f"   🔐 Autenticación: JWT")
        logger.info(f"   📚 Documentación: Swagger/OpenAPI")
        logger.info(f"   🐍 Python: {sys.version.split()[0]}")
        logger.info(f"   📁 Entorno: {os.environ.get('VIRTUAL_ENV', 'Sistema global')}")
        logger.info("=" * 60)
        
        # Iniciar servidor
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug
        )
        
    except ImportError as e:
        logger.error(f"❌ Error importando la aplicación: {e}")
        logger.error("💡 Asegúrate de que todas las dependencias estén instaladas:")
        logger.error("   pip install -r requirements.txt")
        logger.error("   python -m pip install --upgrade pip")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Error inesperado: {e}")
        logger.error("💡 Verifica que:")
        logger.error("   1. Estés en el directorio raíz del proyecto")
        logger.error("   2. El entorno virtual esté activado")
        logger.error("   3. Todas las dependencias estén instaladas")
        sys.exit(1)

if __name__ == "__main__":
    main()
