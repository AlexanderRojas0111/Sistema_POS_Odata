# 🐳 Sistema POS Sabrositas v2.0.0 - Guía Docker

## 📋 Configuración Docker Optimizada - Las Arepas Cuadradas

## 📋 Configuración Docker Optimizada

### ✅ Archivos Docker Esenciales - Actualizados 2024

**🐳 Dockerfiles Optimizados:**
- `Dockerfile` - Imagen principal optimizada (Python 3.13 Alpine)
- `Dockerfile.enterprise` - Multi-stage build para producción enterprise

**🔧 Docker Compose Configurations:**
- `docker-compose.yml` - Configuración principal (SQLite + Redis)
- `docker-compose.production.yml` - Configuración de producción (PostgreSQL)
- `docker-compose.enterprise.yml` - Configuración enterprise completa

**📁 Archivos de Configuración:**
- `.dockerignore` - Contexto optimizado (75% más rápido)
- `docker-start.ps1` - Script de inicio automatizado
- `requirements.txt` - Dependencias actualizadas a versiones 2024

### 🚀 Inicio Rápido

#### Opción 1: Script Automatizado (Recomendado)
```powershell
.\docker-start.ps1
```

#### Opción 2: Comandos Manuales
```bash
# Construir e iniciar
docker compose up -d --build

# Verificar estado
docker compose ps

# Ver logs
docker compose logs -f
```

### 🏗️ Arquitectura de Contenedores

#### Configuración Principal (`docker-compose.yml`)
- **sabrositas-app**: Aplicación Flask (Puerto 8000)
- **redis**: Cache y rate limiting
- **Volúmenes**: Logs, datos, instancia SQLite

#### Configuración Enterprise (`docker-compose.enterprise.yml`)
- **pos-api**: Aplicación principal
- **postgres**: Base de datos PostgreSQL
- **redis**: Cache y sesiones
- **nginx**: Proxy reverso y load balancer
- **grafana**: Monitoreo y métricas
- **prometheus**: Recolección de métricas

### 🔧 Variables de Entorno

#### Principales
```env
FLASK_ENV=production
DATABASE_URL=sqlite:///instance/pos_odata.db
SECRET_KEY=sabrositas-secret-key-2024
JWT_SECRET_KEY=sabrositas-jwt-secret-2024
HOST=0.0.0.0
PORT=8000
```

#### Enterprise
```env
DB_PASSWORD=enterprise_password_123
REDIS_PASSWORD=redis_enterprise_123
JWT_SECRET_KEY=jwt_enterprise_secret_123
```

### 📊 Monitoreo y Salud

#### Health Checks
- **Backend**: `http://localhost:8000/api/v1/health`
- **Redis**: Ping automático cada 30s
- **Intervalo**: 30s timeout 10s, 3 reintentos

#### Logs
```bash
# Ver todos los logs
docker compose logs -f

# Logs específicos del backend
docker compose logs -f sabrositas-app

# Logs de Redis
docker compose logs -f redis
```

### 🛠️ Comandos Útiles

#### Gestión de Contenedores
```bash
# Iniciar servicios
docker compose up -d

# Detener servicios
docker compose down

# Reiniciar servicios
docker compose restart

# Reconstruir imagen
docker compose build --no-cache

# Ver estado
docker compose ps
```

#### Mantenimiento
```bash
# Limpiar contenedores parados
docker container prune

# Limpiar imágenes no utilizadas
docker image prune

# Limpiar volúmenes no utilizados
docker volume prune

# Limpiar todo el sistema
docker system prune -a
```

#### Acceso a Contenedores
```bash
# Shell en el contenedor principal
docker compose exec sabrositas-app /bin/sh

# Shell en Redis
docker compose exec redis redis-cli

# Ver procesos
docker compose top
```

### 🔒 Seguridad

#### Características de Seguridad
- ✅ Usuario no-root en contenedores
- ✅ Imagen Alpine Linux (mínima superficie de ataque)
- ✅ Variables de entorno para secretos
- ✅ Red Docker aislada
- ✅ Health checks automáticos
- ✅ Reinicio automático de contenedores

#### Configuración Segura
```yaml
# Ejemplo de configuración segura
environment:
  - SECRET_KEY=${SECRET_KEY:-generate-secure-key}
  - JWT_SECRET_KEY=${JWT_SECRET_KEY:-generate-jwt-key}
  - DB_PASSWORD=${DB_PASSWORD:-secure-password}
```

### 📈 Escalabilidad

#### Configuración de Recursos
```yaml
deploy:
  resources:
    limits:
      cpus: '1.0'
      memory: 1G
    reservations:
      cpus: '0.5'
      memory: 512M
```

#### Réplicas (Enterprise)
```yaml
deploy:
  replicas: 3
  update_config:
    parallelism: 1
    delay: 10s
  restart_policy:
    condition: on-failure
```

### 🐛 Solución de Problemas

#### Problemas Comunes

**Puerto ocupado:**
```bash
# Verificar qué usa el puerto 8000
netstat -tulpn | grep 8000

# Cambiar puerto en docker-compose.yml
ports:
  - "8001:8000"
```

**Permisos de volúmenes:**
```bash
# Verificar permisos
ls -la logs/ data/ instance/

# Corregir permisos si es necesario
sudo chown -R 1000:1000 logs/ data/ instance/
```

**Memoria insuficiente:**
```bash
# Verificar uso de memoria
docker stats

# Aumentar límites en docker-compose.yml
mem_limit: 2g
```

### 📋 Checklist de Verificación

#### Antes del Despliegue
- [ ] Docker y Docker Compose instalados
- [ ] Puertos 8000 y 6379 disponibles
- [ ] Permisos de directorios correctos
- [ ] Variables de entorno configuradas
- [ ] Archivos .env actualizados

#### Después del Despliegue
- [ ] Health check responde OK
- [ ] Logs sin errores críticos
- [ ] Base de datos accesible
- [ ] Redis funcionando
- [ ] API endpoints responden

### 🎯 URLs de Verificación

Una vez iniciado el sistema:

- **Health Check**: http://localhost:8000/api/v1/health
- **API Products**: http://localhost:8000/api/v1/products
- **API Auth**: http://localhost:8000/api/v1/auth/login

### 🥟 ¡Sistema Docker Optimizado para Arepas Cuadradas!

El sistema está configurado para máximo rendimiento y facilidad de despliegue con Docker.
