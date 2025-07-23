# Proyecto Inventario

Este es un sistema de gestión de inventario desarrollado en Python (Flask) y React.

## Estructura del Proyecto

- `app/`: Backend Flask
- `frontend/`: Frontend React
- `scripts/`: Scripts de migración, carga, limpieza y exportación de datos
- `data/`: Archivos de datos de ejemplo y exportaciones
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
   python -m scripts.migrate_db
   python -m scripts.load_sample_data
   python -m scripts.load_sample_users
   python -m scripts.load_sample_customers_and_sales
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

## Scripts de gestión de base de datos

- **Migración:**
  - `python -m scripts.migrate_db` — Borra y recrea todas las tablas según los modelos actuales.

- **Carga de datos de ejemplo:**
  - `python -m scripts.load_sample_data` — Carga productos desde `data/products.csv`.
  - `python -m scripts.load_sample_users` — Carga usuarios de ejemplo.
  - `python -m scripts.load_sample_customers_and_sales` — Carga clientes y ventas de ejemplo.

- **Limpieza de datos:**
  - `python -m scripts.clean_sales` — Elimina todas las ventas.
  - `python -m scripts.clean_customers` — Elimina todos los clientes.
  - `python -m scripts.clean_products` — Elimina todos los productos.
  - `python -m scripts.clean_inventory` — Elimina todos los movimientos de inventario.

- **Exportación de datos:**
  - `python -m scripts.export_sales_to_csv` — Exporta todas las ventas a `data/exported_sales.csv`.
  - `python -m scripts.export_products_to_csv` — Exporta todos los productos a `data/exported_products.csv`.
  - `python -m scripts.export_inventory_to_csv` — Exporta todos los movimientos de inventario a `data/exported_inventory.csv`.

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
- `GET /api/sales/<sale_id>/pdf` - Descarga la factura/recibo en PDF de una venta

## Contribuciones

¡Las contribuciones son bienvenidas! Abre un issue o haz un pull request.

## Licencia


© 2024 O'data Company. Todos los derechos reservados.

**Desarrollador Principal:** Alexander Rojas - Director de Desarrollo y Software

Este proyecto es propiedad de O'data Company. El uso, distribución o modificación de este código requiere autorización explícita por escrito de O'data Company.

Para consultas sobre licenciamiento y permisos, contactar a: [alexrojas8211@gmail.com]

---

### Términos de Uso

- ✅ Uso permitido para revisión y evaluación
- ❌ Prohibida la redistribución sin autorización
- ❌ Prohibido el uso comercial sin licencia
- ❌ Prohibida la modificación sin permiso

---

**Nota:** Si deseas utilizar este proyecto bajo una licencia específica (MIT, Apache 2.0, GPL, etc.), contacta con el equipo de desarrollo de O'data Company.

