#!/usr/bin/env python3
"""
Servidor de desarrollo para Sistema POS O'data
Compatible con Windows y Linux
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

def main():
    """Función principal del servidor"""
    try:
        # Verificar que estamos en el directorio correcto
        if not Path('app').exists():
            logger.error("Directorio 'app' no encontrado. Ejecuta desde la raíz del proyecto.")
            sys.exit(1)
        
        # Importar la aplicación
        from app import create_app
        
        # Crear la aplicación Flask
        app = create_app('development')
        
        # Configuración del servidor
        host = os.environ.get('FLASK_HOST', '127.0.0.1')
        port = int(os.environ.get('FLASK_PORT', 5000))
        debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
        
        logger.info("🚀 INICIANDO SERVIDOR POS ODATA")
        logger.info("=" * 50)
        logger.info(f"🌐 Host: {host}")
        logger.info(f"🔌 Puerto: {port}")
        logger.info(f"🐛 Debug: {debug}")
        logger.info(f"📁 Directorio: {os.getcwd()}")
        logger.info("=" * 50)
        
        # Iniciar servidor
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug
        )
        
    except ImportError as e:
        logger.error(f"Error importando la aplicación: {e}")
        logger.error("Asegúrate de que todas las dependencias estén instaladas")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
