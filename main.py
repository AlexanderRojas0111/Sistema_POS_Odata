#!/usr/bin/env python3
"""
Sistema POS O'Data v2.0.0 - Punto de Entrada Principal
=====================================================
Aplicación enterprise con arquitectura robusta y profesional.
"""

import os
import sys
import logging
from app import create_app

# Configurar logging antes de crear la app
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Función principal para ejecutar la aplicación enterprise"""
    try:
        # Crear aplicación con configuración enterprise
        app = create_app('production')
        
        # Configuración del servidor
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 8000))
        debug = os.environ.get('FLASK_ENV') == 'development'
        
        logger.info("=" * 60)
        logger.info("SISTEMA POS O'DATA v2.0.0 - ENTERPRISE ARCHITECTURE")
        logger.info("=" * 60)
        logger.info(f"Host: {host}")
        logger.info(f"Port: {port}")
        logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'production')}")
        logger.info(f"Debug Mode: {debug}")
        logger.info("=" * 60)
        
        # Iniciar servidor
        app.run(host=host, port=port, debug=debug)
        
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
