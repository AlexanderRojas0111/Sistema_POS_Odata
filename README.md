# Sistema de Gestión de Inventario con IA

Este sistema de gestión de inventario incorpora tecnologías avanzadas de IA para proporcionar funcionalidades inteligentes de búsqueda, automatización y análisis.

## Características Principales

- **Búsqueda Semántica (RAG)**
  - Búsqueda inteligente de productos por significado
  - Recomendaciones contextuales
  - Análisis de inventario basado en patrones

- **Agentes Autónomos (A2A)**
  - Monitoreo proactivo de stock
  - Automatización de pedidos
  - Optimización de inventario

- **Comunicación entre Modelos (MCP)**
  - Intercambio estructurado de información
  - Coordinación entre componentes de IA
  - Gestión de contexto inteligente

- **Funcionalidades Tradicionales**
  - Gestión de productos
  - Control de inventario
  - Registro de ventas
  - Gestión de usuarios
  - Generación de reportes

## Requisitos Técnicos

- Python 3.9+
- SQLite (desarrollo) / PostgreSQL (producción)
- Redis
- Node.js y npm (para el frontend)

## Instalación

1. Clonar el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd proyecto-inventario-1
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Unix:
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
Crear archivo `.env` con:
```
FLASK_APP=app.main:app
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///instance/app.db
SECRET_KEY=tu_clave_secreta
JWT_SECRET_KEY=tu_jwt_secreto
```

5. Inicializar la base de datos:
```bash
flask db upgrade
```

6. Cargar datos de ejemplo (opcional):
```bash
python scripts/load_sample_data.py
```

## Estructura del Proyecto

```
proyecto-inventario-1/
├── app/
│   ├── crud/          # Operaciones CRUD
│   ├── models/        # Modelos de datos
│   ├── routes/        # Rutas de la API
│   ├── rag/           # Módulos de búsqueda semántica
│   ├── agents/        # Sistema de agentes autónomos
│   └── mcp/           # Protocolo de comunicación
├── frontend/          # Aplicación React
├── scripts/          # Scripts de utilidad
└── tests/           # Pruebas unitarias y de integración
```

## API Endpoints

### Búsqueda Semántica
- `GET /api/search/semantic` - Búsqueda semántica de productos
- `GET /api/search/hybrid` - Búsqueda híbrida (semántica + tradicional)
- `POST /api/embeddings` - Generación de embeddings

### Gestión de Agentes
- `GET /api/agents` - Listar agentes activos
- `POST /api/agents/{id}/tasks` - Asignar tareas a agentes
- `GET /api/agents/status` - Estado del sistema de agentes

### Productos e Inventario
- `GET /api/products` - Listar productos
- `POST /api/products` - Crear producto
- `GET /api/inventory` - Estado del inventario
- `POST /api/sales` - Registrar venta

## Seguridad

- Autenticación JWT
- Control de acceso basado en roles
- Validación de datos con Pydantic
- Sanitización de entradas
- Rate limiting

## Monitoreo

- Métricas de rendimiento con Prometheus
- Trazabilidad con OpenTelemetry
- Logs de actividad de agentes
- Alertas automáticas

## Desarrollo

### Ejecutar Tests
```bash
pytest
```

### Ejecutar en Desarrollo
```bash
flask run
```

### Generar Migraciones
```bash
flask db migrate -m "Descripción del cambio"
flask db upgrade
```

## Contribuir

1. Fork el repositorio
2. Crear rama para feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'feat: Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## Licencia

[Tipo de Licencia]

