# Proyecto Inventario

Este es un sistema de gestión de inventario desarrollado en Python (Flask) y React.

## Estructura del Proyecto

- `app/`: Backend Flask
- `frontend/`: Frontend React
- `scripts/`: Scripts de migración y carga
- `data/`: Archivos de datos de ejemplo
- `tests/`: Pruebas automáticas
- `requirements.txt`: Dependencias Python
- `Dockerfile`: Imagen para despliegue con Docker
- `.gitignore`: Archivos y carpetas ignorados por Git

## Instalación y Uso Local

1. Clona el repositorio:
   ```bash
   git clone https://github.com/AlexanderRojas0111/Sistema_POS_Odata.git
   cd Sistema_POS_Odata
   ```
2. Instala las dependencias de Python:
   ```bash
   pip install -r requirements.txt
   ```
3. Crea el archivo `.env` en la raíz con la configuración necesaria:
   ```env
   SECRET_KEY=tu_clave_secreta
   SQLALCHEMY_DATABASE_URI=sqlite:///instance/inventario.db
   SQLALCHEMY_TRACK_MODIFICATIONS=False
   JWT_SECRET_KEY=otra_clave_secreta
   ```
4. Ejecuta migraciones y carga de datos:
   ```bash
   python scripts/migrate_db.py
   python scripts/load_sample_data.py
   ```
5. Ejecuta el backend:
   ```bash
   python -m app.main
   ```
6. Instala Node.js y npm si no los tienes ([descargar aquí](https://nodejs.org/)).
7. Inicializa el frontend:
   ```bash
   cd frontend
   npm install
   npm start
   ```

## Uso con Docker

1. Instala [Docker Desktop](https://www.docker.com/products/docker-desktop/).
2. Construye la imagen:
   ```bash
   docker build -t inventario-app .
   ```
3. Ejecuta el contenedor:
   ```bash
   docker run -p 5000:5000 inventario-app
   ```

## Documentación OpenAPI

- Accede a la documentación interactiva en: [http://localhost:5000/docs](http://localhost:5000/docs)
- La documentación se genera automáticamente con Flask-RESTX.

## Pruebas

Ejecuta los tests con:
```bash
pytest
```

## Subir el proyecto a GitHub

1. Inicializa el repositorio (si no lo has hecho):
   ```bash
   git init
   ```
2. Configura el remoto:
   ```bash
   git remote set-url origin https://github.com/AlexanderRojas0111/Sistema_POS_Odata.git
   # o si no existe:
   # git remote add origin https://github.com/AlexanderRojas0111/Sistema_POS_Odata.git
   ```
3. Agrega los archivos y haz commit:
   ```bash
   git add .
   git commit -m "Proyecto inventario inicial con backend Flask y frontend React"
   ```
4. Sube el proyecto:
   ```bash
   git branch -M main
   git push -u origin main
   ```
5. Invita a tu equipo desde GitHub en Settings > Collaborators.

## .gitignore recomendado

- Ignora entornos virtuales, archivos sensibles, bases de datos locales y dependencias de Node/React.

## Ejemplo de Endpoints

- `GET /api/users/` - Lista todos los usuarios
- `POST /api/users/` - Crea un usuario
- `GET /api/products/` - Lista todos los productos
- `POST /api/products/` - Crea un producto

## Contribuciones

¡Las contribuciones son bienvenidas! Abre un issue o haz un pull request.

## Licencia

MIT
