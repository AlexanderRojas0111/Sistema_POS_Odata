from app import create_app
from app.core.config import config

app = create_app()

if __name__ == "__main__":
    # Usar la configuración del archivo config.py
    app.run(
        debug=False,  # Cambiado a False para evitar error de watchdog en Windows
        host=app.config.get('SERVER_HOST', '127.0.0.1'),
        port=app.config.get('SERVER_PORT', 8000)
    ) 