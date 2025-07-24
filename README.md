# Sistema de Gestión de Inventario con IA

Sistema profesional de gestión de inventario que incorpora tecnologías avanzadas de IA para proporcionar funcionalidades inteligentes de búsqueda, automatización y análisis.

## Características Principales

### Funcionalidades Tradicionales
- Gestión completa de productos e inventario
- Sistema de ventas y facturación
- Gestión de usuarios y roles
- Reportes y análisis

### Características Avanzadas de IA
- **Búsqueda Semántica (RAG)**
  - Búsqueda inteligente por significado
  - Recomendaciones contextuales
  - Análisis de patrones

- **Sistema de Agentes (A2A)**
  - Monitoreo automático de stock
  - Alertas predictivas
  - Optimización de inventario

- **Protocolo de Comunicación (MCP)**
  - Integración inteligente entre módulos
  - Gestión avanzada de contexto
  - Comunicación estructurada

## Requisitos Técnicos

- Python 3.9+
- PostgreSQL 13+ (Producción)
- Redis 6+
- Node.js 14+ (Frontend)
- Docker y Docker Compose (Despliegue)

## Instalación

### Desarrollo Local

1. Clonar el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd proyecto-inventario-1
```

2. Crear y activar entorno virtual:
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Unix
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

5. Inicializar la base de datos:
```bash
flask db upgrade
python scripts/init_db.py
```

### Despliegue con Docker

1. Asegurarse de tener Docker y Docker Compose instalados

2. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con configuraciones de producción
```

3. Ejecutar el script de despliegue:
```bash
chmod +x deploy.sh
./deploy.sh
```

## Estructura del Proyecto

```
proyecto-inventario-1/
├── app/
│   ├── api/            # Endpoints API (v1 y v2)
│   ├── core/           # Configuración central
│   ├── models/         # Modelos de datos
│   ├── services/       # Lógica de negocio
│   └── utils/          # Utilidades
├── docs/              # Documentación
├── frontend/         # Aplicación React
├── scripts/         # Scripts de utilidad
└── tests/          # Pruebas
```

## API Endpoints

### API v1 (Tradicional)
- `GET /api/v1/products` - Listar productos
- `POST /api/v1/products` - Crear producto
- `GET /api/v1/inventory` - Estado del inventario
- `POST /api/v1/sales` - Registrar venta

### API v2 (IA)
- `GET /api/v2/search/semantic` - Búsqueda semántica
- `GET /api/v2/search/hybrid` - Búsqueda híbrida
- `GET /api/v2/agents/status` - Estado de agentes

## Monitoreo y Mantenimiento

### Dashboards
- Grafana: `http://localhost:3000`
- Prometheus: `http://localhost:9090`

### Logs
- Aplicación: `./logs/app.log`
- Acceso: `./logs/access.log`

## Seguridad

- Autenticación JWT
- Roles y permisos granulares
- Encriptación de datos sensibles
- Rate limiting
- Validación de entrada

## Contribuir

1. Fork el repositorio
2. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
3. Commit cambios: `git commit -am 'feat: Agregar nueva funcionalidad'`
4. Push a la rama: `git push origin feature/nueva-funcionalidad`
5. Crear Pull Request

## Licencia

Este proyecto está licenciado bajo los términos de la licencia MIT.

