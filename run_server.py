#!/usr/bin/env python3
"""
Script para ejecutar el servidor POS en modo producción
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def run_production_server():
    """Ejecutar servidor en modo producción"""
    from app import create_app
    
    # Configurar variables de entorno para producción
    os.environ['FLASK_ENV'] = 'development'  # Usar development con SQLite por simplicidad
    
    # Crear aplicación
    app = create_app('development')
    
    print("🚀 INICIANDO SERVIDOR POS ODATA")
    print("=" * 50)
    print(f"🌐 URL: http://localhost:5000")
    print(f"📊 Health Check: http://localhost:5000/health")
    print(f"🔧 API: http://localhost:5000/api/v1/")
    print(f"📖 Documentación: Disponible en endpoints individuales")
    print("=" * 50)
    print("✅ Servidor listo - Presiona Ctrl+C para detener")
    print()
    
    try:
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print(f"❌ Error ejecutando servidor: {e}")

if __name__ == '__main__':
    run_production_server()
