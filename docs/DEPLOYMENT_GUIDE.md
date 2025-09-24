# 🚀 Guía de Despliegue - Sistema POS O'data

## 📋 Resumen del Sistema

El Sistema POS O'data v2.0.0 es una aplicación web moderna con las siguientes características:

- **Backend**: Flask 3.1.1 con Python 3.13
- **Base de Datos**: PostgreSQL 15.14
- **Cache**: Redis 7-alpine
- **IA/ML**: scikit-learn para búsqueda semántica
- **Contenedores**: Docker + Docker Compose
- **Backup**: Automático diario con retención

## 🏗️ Arquitectura de Despliegue

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Base de Datos │
│   (React)       │◄──►│   (Flask)       │◄──►│   (PostgreSQL)  │
│   Port: 80      │    │   Port: 5000    │    │   Port: 5432    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Cache         │
                       │   (Redis)       │
                       │   Port: 6379    │
                       └─────────────────┘
```

## 🐳 Despliegue con Docker Compose

### 1. Prerrequisitos

- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM mínimo
- 10GB espacio en disco

### 2. Configuración Inicial

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/sistema-pos-odata.git
cd sistema-pos-odata

# Copiar configuración de producción
cp env.production .env

# Editar variables de entorno
nano .env
```

### 3. Variables de Entorno Críticas

```env
# Base de Datos
POSTGRES_DB=pos_db_production
POSTGRES_USER=pos_user
POSTGRES_PASSWORD=your_secure_password_here

# Redis
REDIS_PASSWORD=your_redis_password_here

# Seguridad
SECRET_KEY=your-super-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Docker
APP_IMAGE_NAME=pos-odata-app
APP_IMAGE_TAG=latest
```

### 4. Despliegue

```bash
# Construir imágenes
docker compose -f docker-compose.production.yml build

# Levantar servicios
docker compose -f docker-compose.production.yml up -d

# Verificar estado
docker compose -f docker-compose.production.yml ps
```

## 🔧 Servicios Incluidos

### pos-odata-app
- **Imagen**: pos-odata-app:latest
- **Puerto**: 5000
- **Funciones**: API Flask, migraciones automáticas
- **Health Check**: http://localhost:5000/health

### pos-odata-db
- **Imagen**: postgres:15-alpine
- **Puerto**: 5432
- **Funciones**: Base de datos principal
- **Optimizaciones**: Índices en FKs, extensiones habilitadas

### pos-odata-redis
- **Imagen**: redis:7-alpine
- **Puerto**: 6379
- **Funciones**: Cache y sesiones

### pos-odata-backup
- **Imagen**: postgres:15-alpine
- **Funciones**: Backup manual de BD
- **Frecuencia**: Bajo demanda

### pos-odata-backup-cron
- **Imagen**: bitnami/cron:latest
- **Funciones**: Backup automático diario
- **Horario**: 02:00 UTC

## 📊 Monitoreo y Logs

### Health Checks

```bash
# Estado general
curl http://localhost:5000/health

# Logs en tiempo real
docker compose -f docker-compose.production.yml logs -f

# Logs específicos
docker compose -f docker-compose.production.yml logs -f app
```

### Métricas de Sistema

```bash
# Uso de recursos
docker stats

# Espacio en disco
docker system df

# Estado de contenedores
docker compose -f docker-compose.production.yml ps
```

## 🔄 Backup y Recuperación

### Backup Automático

El sistema incluye backup automático configurado:

- **Frecuencia**: Diario a las 02:00
- **Retención**: 30 días
- **Ubicación**: `./backups/`
- **Formato**: SQL comprimido (.sql.gz)

### Backup Manual

```bash
# Ejecutar backup inmediato
docker compose -f docker-compose.production.yml run --rm backup

# Ver archivos de backup
ls -la backups/
```

### Restauración

```bash
# Restaurar desde backup
docker exec -i pos-odata-db psql -U pos_user -d pos_db_production < backups/pos_db_backup_YYYYMMDD_HHMMSS.sql
```

## 🛠️ Mantenimiento

### Actualizaciones

```bash
# Actualizar código
git pull origin main

# Reconstruir y redesplegar
docker compose -f docker-compose.production.yml down
docker compose -f docker-compose.production.yml build
docker compose -f docker-compose.production.yml up -d
```

### Limpieza

```bash
# Limpiar contenedores parados
docker container prune

# Limpiar imágenes no utilizadas
docker image prune

# Limpiar volúmenes no utilizados
docker volume prune
```

### Logs

```bash
# Rotar logs
docker compose -f docker-compose.production.yml logs --tail=1000 > logs/app.log

# Limpiar logs antiguos
find logs/ -name "*.log" -mtime +7 -delete
```

## 🔐 Seguridad

### Configuración de Red

- **Puertos expuestos**: 5000 (app), 5432 (db), 6379 (redis)
- **Red interna**: pos-network (bridge)
- **Aislamiento**: Contenedores aislados

### Variables de Entorno

- **Contraseñas**: Cambiar todas las contraseñas por defecto
- **Claves**: Generar nuevas claves secretas
- **CORS**: Configurar orígenes permitidos

### Backup de Seguridad

- **Frecuencia**: Diario
- **Retención**: 30 días
- **Encriptación**: Opcional (configurar en .env)

## 📈 Escalabilidad

### Recursos Mínimos

- **CPU**: 2 cores
- **RAM**: 4GB
- **Disco**: 10GB

### Recursos Recomendados

- **CPU**: 4 cores
- **RAM**: 8GB
- **Disco**: 50GB

### Escalado Horizontal

Para mayor carga, considerar:

1. **Load Balancer**: Nginx o HAProxy
2. **Múltiples instancias**: Replicar contenedor app
3. **Base de datos**: PostgreSQL con réplicas
4. **Cache**: Redis Cluster

## 🚨 Troubleshooting

### Problemas Comunes

**Contenedor no inicia:**
```bash
# Ver logs
docker compose -f docker-compose.production.yml logs app

# Verificar configuración
docker compose -f docker-compose.production.yml config
```

**Base de datos no conecta:**
```bash
# Verificar estado
docker compose -f docker-compose.production.yml logs db

# Probar conexión
docker exec -it pos-odata-db psql -U pos_user -d pos_db_production
```

**Backup no funciona:**
```bash
# Verificar permisos
ls -la backups/

# Ejecutar manualmente
docker compose -f docker-compose.production.yml run --rm backup
```

### Logs Importantes

```bash
# Logs de aplicación
tail -f logs/app.log

# Logs de Docker
docker compose -f docker-compose.production.yml logs -f

# Logs del sistema
journalctl -u docker
```

## 📞 Soporte

- **Documentación**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/tu-usuario/sistema-pos-odata/issues)
- **Email**: soporte@pos-odata.com

---

**Última actualización**: 23 de septiembre de 2025
**Versión**: 2.0.0
