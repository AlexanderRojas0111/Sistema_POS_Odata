# Sistema de Gestión de Inventario con IA

Este sistema de gestión de inventario incorpora tecnologías avanzadas de IA para proporcionar funcionalidades inteligentes de búsqueda, automatización y análisis.

## Características Principales

### RAG (Retrieval Augmented Generation)
- Búsqueda semántica de productos
- Recomendaciones contextuales
- Análisis inteligente de inventario

### A2A (Agent-to-Agent)
- Automatización de procesos de inventario
- Monitoreo proactivo de stock
- Comunicación entre agentes autónomos

### Sistema de Mensajería
- Comunicación en tiempo real
- Estado distribuido
- Logging centralizado

## Requisitos del Sistema

### Software Necesario
- Python 3.9+
- PostgreSQL 13+ con extensión pgvector
- Redis 6+
- Node.js 14+ (para el frontend)

### Servicios
- Base de datos PostgreSQL (para vectores)
- Servidor Redis
- Servidor web (producción)

## Instalación

1. Clonar el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd proyecto-inventario-1
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
Crear archivo `.env` con:
```env
FLASK_APP=app
FLASK_ENV=development
DATABASE_URL=sqlite:///instance/app.db
VECTOR_DATABASE_URL=postgresql://usuario:contraseña@localhost/vector_db
REDIS_URL=redis://localhost:6379/0
```

5. Configurar base de datos vectorial:
```bash
python scripts/setup_vector_db.py
```

6. Verificar Redis:
```bash
python scripts/check_redis.py
```

## Estructura del Proyecto

```
proyecto-inventario-1/
├── app/
│   ├── agents/         # Agentes autónomos
│   ├── crud/          # Operaciones CRUD
│   ├── mcp/           # Protocolo de comunicación
│   ├── rag/           # Búsqueda semántica
│   ├── routes/        # Endpoints API
│   └── vector_store/  # Base de datos vectorial
├── frontend/          # Aplicación React
├── scripts/          # Scripts de utilidad
└── tests/            # Pruebas
```

## Uso

### Iniciar el Servidor de Desarrollo
```bash
flask run
```

### Ejecutar Pruebas
```bash
pytest
```

### Endpoints API Principales

#### Búsqueda Semántica
- POST `/api/v2/search/semantic`
- POST `/api/v2/search/hybrid`

#### Gestión de Agentes
- POST `/api/v2/agents`
- GET `/api/v2/agents/{id}`
- POST `/api/v2/agents/{id}/tasks`

## Características de IA

### RAG (Retrieval Augmented Generation)
El sistema utiliza embeddings para:
- Búsqueda semántica de productos
- Recomendaciones basadas en contexto
- Análisis de patrones de inventario

### Agentes Autónomos (A2A)
Los agentes pueden:
- Monitorear niveles de inventario
- Generar alertas automáticas
- Optimizar la gestión de stock

## Seguridad
- Autenticación JWT
- Validación de datos
- Sanitización de entradas
- Logs de auditoría

## Monitoreo
- Métricas de rendimiento
- Logs de agentes
- Estado del sistema en tiempo real

## Contribuir
1. Fork el repositorio
2. Crear rama feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## Licencia
[Especificar la licencia]

