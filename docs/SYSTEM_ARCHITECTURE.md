# 🏗️ Arquitectura del Sistema POS O'data

## 📋 Resumen Ejecutivo

El Sistema POS O'data v2.0.0 es una aplicación web moderna construida con una arquitectura de microservicios containerizada, diseñada para ser escalable, robusta y fácil de mantener.

## 🎯 Principios de Diseño

- **Modularidad**: Separación clara de responsabilidades
- **Escalabilidad**: Diseño preparado para crecimiento
- **Mantenibilidad**: Código limpio y documentado
- **Seguridad**: Múltiples capas de protección
- **Performance**: Optimización en cada capa

## 🏛️ Arquitectura General

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   React App     │  │   Nginx         │  │   Static Files  │ │
│  │   Port: 80      │  │   Load Balancer │  │   Assets        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   Rate Limiting │  │   CORS          │  │   Authentication│ │
│  │   Redis-based   │  │   Headers       │  │   JWT Tokens    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Application Layer                       │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   API v1        │  │   API v2        │  │   AI Services   │ │
│  │   Basic POS     │  │   Advanced      │  │   ML Engine     │ │
│  │   Operations    │  │   Features      │  │   Search        │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Layer                              │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   PostgreSQL    │  │   Redis         │  │   File Storage  │ │
│  │   Primary DB    │  │   Cache         │  │   Uploads       │ │
│  │   Port: 5432    │  │   Port: 6379    │  │   Logs          │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 🔧 Componentes del Sistema

### 1. Frontend (React)

**Tecnologías:**
- React 18.2.0
- Material-UI
- Axios para HTTP
- React Router

**Características:**
- SPA (Single Page Application)
- Responsive Design
- Componentes reutilizables
- Estado global con Context API

### 2. Backend (Flask)

**Tecnologías:**
- Flask 3.1.1
- Python 3.13
- SQLAlchemy 2.0.42
- Flask-JWT-Extended 4.7.1

**Arquitectura:**
```
app/
├── api/
│   ├── v1/          # API básica del POS
│   └── v2/          # API avanzada con IA
├── core/
│   ├── config.py    # Configuraciones
│   └── database.py  # Conexión a BD
├── models/          # Modelos de datos
├── services/        # Lógica de negocio
├── utils/           # Utilidades
└── agents/          # Agentes de IA
```

### 3. Base de Datos (PostgreSQL)

**Configuración:**
- PostgreSQL 15.14
- Pool de conexiones (20 conexiones)
- Índices optimizados
- Extensiones habilitadas

**Esquema:**
```sql
-- Tablas principales
customers          # Clientes
products           # Productos
inventory          # Inventario
sales              # Ventas
sale_items         # Items de venta
users              # Usuarios
product_embeddings # Embeddings para IA
alembic_version    # Control de migraciones
```

**Optimizaciones:**
- Índices en todas las claves foráneas
- Extensiones `pg_stat_statements` y `pg_trgm`
- Configuración de pool de conexiones
- Backup automático diario

### 4. Cache (Redis)

**Configuración:**
- Redis 7-alpine
- Persistencia configurada
- Política de expulsión LRU

**Uso:**
- Cache de sesiones
- Rate limiting
- Cache de consultas frecuentes
- Almacenamiento temporal de datos

### 5. Servicios de IA

**Tecnologías:**
- scikit-learn 1.5.1
- TF-IDF para búsqueda semántica
- Cosine Similarity para recomendaciones
- TruncatedSVD para reducción dimensional

**Funcionalidades:**
- Búsqueda semántica de productos
- Sistema de recomendaciones
- Autocompletado predictivo
- Análisis de texto

## 🐳 Containerización

### Docker Compose

**Servicios:**
```yaml
services:
  app:           # Aplicación Flask
  db:            # PostgreSQL
  redis:         # Redis
  backup:        # Backup manual
  backup-cron:   # Backup automático
```

**Redes:**
- `pos-network`: Red interna para comunicación entre servicios

**Volúmenes:**
- `postgres_data`: Datos persistentes de PostgreSQL
- `redis_data`: Datos persistentes de Redis
- `./backups`: Archivos de backup
- `./logs`: Logs de aplicación

### Imágenes Docker

**pos-odata-app:latest**
- Base: Python 3.13-slim
- Multi-stage build
- Optimizada para producción
- Health checks incluidos

**postgres:15-alpine**
- Base de datos principal
- Configuración optimizada
- Extensiones preinstaladas

**redis:7-alpine**
- Cache y sesiones
- Configuración de persistencia
- Política de memoria LRU

## 🔐 Seguridad

### Autenticación y Autorización

**JWT Tokens:**
- Access tokens (1 hora)
- Refresh tokens (30 días)
- Algoritmo HS256
- Headers seguros

**Roles de Usuario:**
- Admin: Acceso completo
- Manager: Gestión de ventas e inventario
- Employee: Operaciones básicas

### Rate Limiting

**Configuración:**
- 200 requests/día por IP
- 50 requests/hora por IP
- 10 requests/minuto por IP
- Almacenamiento en Redis

### CORS

**Configuración:**
- Orígenes permitidos configurados
- Credenciales habilitadas
- Headers expuestos controlados

## 📊 Monitoreo y Logs

### Health Checks

**Endpoints:**
- `/health`: Estado general del sistema
- `/api/v1/health`: Estado de la API
- Health checks de Docker automáticos

### Logging

**Niveles:**
- DEBUG: Desarrollo
- INFO: Información general
- WARNING: Advertencias
- ERROR: Errores
- CRITICAL: Errores críticos

**Ubicaciones:**
- `logs/app.log`: Logs de aplicación
- `logs/deployment.log`: Logs de despliegue
- `logs/validation.log`: Logs de validación

### Métricas

**Sistema:**
- Uso de CPU y memoria
- Conexiones de base de datos
- Tiempo de respuesta de API
- Uso de cache

## 🔄 Backup y Recuperación

### Estrategia de Backup

**Frecuencia:**
- Diario a las 02:00 UTC
- Retención: 30 días
- Compresión: gzip

**Contenido:**
- Esquema completo de base de datos
- Datos de todas las tablas
- Extensiones y configuraciones
- Metadatos de Alembic

### Procedimientos

**Backup Automático:**
```bash
# Ejecutado por cron diariamente
docker run --rm postgres:15-alpine pg_dump [opciones]
```

**Backup Manual:**
```bash
# Ejecutar bajo demanda
docker compose -f docker-compose.production.yml run --rm backup
```

**Restauración:**
```bash
# Restaurar desde backup
docker exec -i pos-odata-db psql -U pos_user -d pos_db_production < backup.sql
```

## 📈 Escalabilidad

### Escalado Vertical

**Recursos Mínimos:**
- CPU: 2 cores
- RAM: 4GB
- Disco: 10GB

**Recursos Recomendados:**
- CPU: 4 cores
- RAM: 8GB
- Disco: 50GB

### Escalado Horizontal

**Estrategias:**
1. **Load Balancer**: Nginx o HAProxy
2. **Múltiples instancias**: Replicar contenedor app
3. **Base de datos**: PostgreSQL con réplicas
4. **Cache**: Redis Cluster

### Optimizaciones

**Base de Datos:**
- Índices en claves foráneas
- Consultas optimizadas
- Pool de conexiones configurado

**Cache:**
- Cache de consultas frecuentes
- Sesiones en Redis
- Rate limiting distribuido

**Aplicación:**
- Código optimizado
- Lazy loading
- Compresión de respuestas

## 🚀 Despliegue

### Ambientes

**Desarrollo:**
- SQLite para base de datos
- MockRedis para cache
- Logs detallados
- Hot reload habilitado

**Producción:**
- PostgreSQL para base de datos
- Redis para cache
- Logs optimizados
- Health checks activos

### CI/CD

**Pipeline:**
1. **Build**: Construcción de imágenes Docker
2. **Test**: Ejecución de tests automatizados
3. **Deploy**: Despliegue automático
4. **Monitor**: Verificación de salud

## 🔧 Mantenimiento

### Actualizaciones

**Código:**
- Git para control de versiones
- Branches para features
- Pull requests para revisión

**Dependencias:**
- requirements.txt para Python
- package.json para Node.js
- Dockerfile para contenedores

### Monitoreo

**Métricas:**
- Uso de recursos
- Tiempo de respuesta
- Errores y excepciones
- Disponibilidad del servicio

**Alertas:**
- Servicios caídos
- Uso alto de recursos
- Errores críticos
- Backup fallido

---

**Última actualización**: 23 de septiembre de 2025
**Versión**: 2.0.0
