# Proyecto Inventario

Este es un sistema de gestión de inventario desarrollado en Python.

## Estructura del Proyecto

- `app/`: Código principal de la aplicación
- `app/main.py`: Punto de entrada de la app
- `app/models.py`: Modelos de base de datos
- `app/schemas.py`: Esquemas de validación
- `app/crud/`: Lógica de negocio CRUD
- `app/routes/`: Rutas de la API
- `app/utils/`: Utilidades y helpers
- `app/database.py`: Conexión a la base de datos
- `data/`: Archivos de datos de ejemplo
- `tests/`: Pruebas automáticas
- `scripts/`: Scripts de migración y carga
- `requirements.txt`: Dependencias
- `Dockerfile`: Imagen para despliegue con Docker

## Instalación y Uso Local

1. Clona el repositorio:
   ```
   git clone https://github.com/AlexanderRojas0111/proyecto-inventario.git
   ```
2. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```
3. Crea el archivo `.env` con la configuración necesaria:
   ```
   SECRET_KEY=tu_clave_secreta
   SQLALCHEMY_DATABASE_URI=sqlite:///instance/inventario.db
   SQLALCHEMY_TRACK_MODIFICATIONS=False
   JWT_SECRET_KEY=otra_clave_secreta
   ```
4. Ejecuta migraciones y carga de datos:
   ```
   python scripts/migrate_db.py
   python scripts/load_sample_data.py
   ```
5. Ejecuta la app:
   ```
   python -m app.main
   ```

## Uso con Docker

1. Instala [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. Construye la imagen:
   ```
   docker build -t inventario-app .
   ```
3. Ejecuta el contenedor:
   ```
   docker run -p 5000:5000 inventario-app
   ```

## Documentación OpenAPI

- Accede a la documentación interactiva en: [http://localhost:5000/docs](http://localhost:5000/docs)
- La documentación se genera automáticamente con Flask-RESTX.

## Pruebas

Ejecuta los tests con:
```
pytest
```

## Ejemplo de Endpoints

- `GET /api/users/` - Lista todos los usuarios
- `POST /api/users/` - Crea un usuario
- `GET /api/products/` - Lista todos los productos
- `POST /api/products/` - Crea un producto

## Contribuciones

¡Las contribuciones son bienvenidas! Abre un issue o haz un pull request.

## Licencia

MIT
