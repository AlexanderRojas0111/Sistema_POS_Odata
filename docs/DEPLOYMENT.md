# Guía de Despliegue - POS O'data

## 📋 Overview

Esta guía describe cómo desplegar el sistema POS O'data en diferentes entornos: desarrollo, staging y producción.

## 🏗️ Arquitectura de Despliegue

### Entornos Disponibles

1. **Development** - Entorno local para desarrollo
2. **Staging** - Entorno de pruebas previo a producción
3. **Production** - Entorno de producción con alta disponibilidad

### Stack Tecnológico

- **Backend**: Flask + PostgreSQL + Redis
- **Frontend**: React + Nginx
- **Monitoreo**: Prometheus + Grafana + Alertmanager
- **SSL**: Let's Encrypt con Certbot
- **Contenedores**: Docker + Docker Compose

## 🚀 Despliegue Rápido

### Prerrequisitos

```bash
# Instalar Docker y Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar herramientas adicionales
sudo apt-get update
sudo apt-get install -y curl git make
```

### Despliegue Local (Desarrollo)

```bash
# Clonar el repositorio
git clone https://github.com/AlexanderRojas0111/Sistema_POS_Odata.git
cd Sistema_POS_Odata

# Configurar variables de entorno
cp env.staging env.local
# Editar env.local con tus configuraciones

# Ejecutar
docker-compose up -d
```

## 🔧 Configuración de Entornos

### 1. Staging

#### Configuración

```bash
# Copiar archivo de configuración
cp env.staging env.staging.local

# Editar variables críticas
nano env.staging.local
```

#### Variables Importantes

```bash
# Base de datos
POSTGRES_PASSWORD=tu_password_seguro
POSTGRES_DB=pos_odata_staging

# Aplicación
SECRET_KEY=tu_secret_key_muy_seguro
JWT_SECRET_KEY=tu_jwt_secret_key_muy_seguro

# Dominio
DOMAIN_NAME=staging.tudominio.com
```

#### Despliegue

```bash
# Despliegue automático
./scripts/deploy-staging.sh

# Con limpieza de Docker
./scripts/deploy-staging.sh --clean
```

#### Verificación

```bash
# Health check
curl http://localhost:5000/health

# Verificar servicios
docker-compose -f docker-compose.staging.yml ps

# Ver logs
docker-compose -f docker-compose.staging.yml logs -f
```

### 2. Producción

#### Configuración

```bash
# Copiar archivo de configuración
cp env.production env.production.local

# Editar TODAS las variables críticas
nano env.production.local
```

#### Variables Críticas de Producción

```bash
# ⚠️ CAMBIAR TODAS ESTAS VARIABLES EN PRODUCCIÓN

# Base de datos
POSTGRES_PASSWORD=password_super_seguro_64_caracteres
POSTGRES_DB=pos_odata_production
POSTGRES_USER=pos_odata_user

# Aplicación
SECRET_KEY=secret_key_super_seguro_64_caracteres_aleatorio
JWT_SECRET_KEY=jwt_secret_key_super_seguro_64_caracteres_aleatorio

# Redis
REDIS_PASSWORD=redis_password_super_seguro

# Dominio
DOMAIN_NAME=pos-odata.com

# Sentry (para monitoreo de errores)
SENTRY_DSN=https://tu-sentry-dsn@sentry.io/project-id
```

#### Despliegue

```bash
# Despliegue con confirmación
./scripts/deploy-production.sh

# Despliegue forzado (sin confirmación)
./scripts/deploy-production.sh --force

# Despliegue con limpieza
./scripts/deploy-production.sh --clean
```

#### Verificación de Producción

```bash
# Health check
curl https://pos-odata.com/health

# Verificar SSL
curl -I https://pos-odata.com

# Verificar servicios
docker-compose -f docker-compose.production.yml ps

# Monitoreo
curl http://localhost:9090  # Prometheus
curl http://localhost:3001  # Grafana
```

## 📊 Monitoreo y Alertas

### Prometheus

- **URL**: http://localhost:9090 (staging) / http://localhost:9090 (production)
- **Métricas**: CPU, memoria, requests, errores, latencia

### Grafana

- **URL**: http://localhost:3002 (staging) / http://localhost:3001 (production)
- **Usuario**: admin
- **Contraseña**: Configurada en variables de entorno

### Alertmanager

- **URL**: http://localhost:9093 (solo producción)
- **Alertas**: Caída de servicios, alto uso de recursos, errores

## 🔐 Seguridad

### SSL/TLS

```bash
# Configurar SSL automático con Let's Encrypt
# Se configura automáticamente en producción

# Verificar certificado
openssl s_client -connect pos-odata.com:443 -servername pos-odata.com
```

### Variables de Entorno

```bash
# Generar claves seguras
openssl rand -hex 32  # Para SECRET_KEY
openssl rand -hex 32  # Para JWT_SECRET_KEY

# Generar contraseñas seguras
openssl rand -base64 32  # Para POSTGRES_PASSWORD
```

### Firewall

```bash
# Configurar firewall (Ubuntu/Debian)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

## 🛠️ Mantenimiento

### Backups

```bash
# Backup manual de base de datos
docker exec pos-odata-prod-db pg_dump -U $POSTGRES_USER $POSTGRES_DB > backup_$(date +%Y%m%d).sql

# Backup automático (configurado en scripts)
# Se ejecuta automáticamente antes de cada despliegue
```

### Logs

```bash
# Ver logs de aplicación
docker-compose -f docker-compose.production.yml logs -f app

# Ver logs de nginx
docker-compose -f docker-compose.production.yml logs -f production-nginx

# Ver logs de base de datos
docker-compose -f docker-compose.production.yml logs -f production-db
```

### Actualizaciones

```bash
# Actualizar aplicación
git pull origin main
./scripts/deploy-production.sh

# Actualizar dependencias
docker-compose -f docker-compose.production.yml build --no-cache
./scripts/deploy-production.sh --clean
```

## 🚨 Troubleshooting

### Problemas Comunes

#### 1. Servicios no inician

```bash
# Verificar logs
docker-compose -f docker-compose.production.yml logs

# Verificar variables de entorno
docker-compose -f docker-compose.production.yml config

# Reiniciar servicios
docker-compose -f docker-compose.production.yml restart
```

#### 2. Base de datos no conecta

```bash
# Verificar estado
docker exec pos-odata-prod-db pg_isready -U $POSTGRES_USER

# Verificar logs
docker logs pos-odata-prod-db

# Reiniciar base de datos
docker-compose -f docker-compose.production.yml restart production-db
```

#### 3. SSL no funciona

```bash
# Verificar certificados
ls -la certbot/conf/live/pos-odata.com/

# Renovar certificados
docker exec production-certbot certbot renew

# Verificar nginx
docker exec production-nginx nginx -t
```

#### 4. Alto uso de recursos

```bash
# Ver métricas
docker stats

# Ver logs de errores
docker-compose -f docker-compose.production.yml logs app | grep ERROR

# Escalar servicios
docker-compose -f docker-compose.production.yml up -d --scale app=5
```

### Recuperación de Desastres

```bash
# Restaurar desde backup
docker exec -i pos-odata-prod-db psql -U $POSTGRES_USER $POSTGRES_DB < backup_20231201.sql

# Rollback a versión anterior
git checkout HEAD~1
./scripts/deploy-production.sh --force

# Restaurar volúmenes
docker volume restore pos-odata_production-postgres-data backup.tar
```

## 📈 Escalabilidad

### Escalado Horizontal

```bash
# Escalar aplicación
docker-compose -f docker-compose.production.yml up -d --scale app=5

# Escalar frontend
docker-compose -f docker-compose.production.yml up -d --scale production-frontend=3
```

### Load Balancing

- Nginx configura automáticamente load balancing
- Prometheus monitorea todas las instancias
- Grafana muestra métricas agregadas

### Base de Datos

```bash
# Configurar réplica de lectura
# Agregar en docker-compose.production.yml:
production-db-replica:
  image: postgres:13
  environment:
    POSTGRES_DB: $POSTGRES_DB
    POSTGRES_USER: $POSTGRES_USER
    POSTGRES_PASSWORD: $POSTGRES_PASSWORD
  volumes:
    - production-postgres-replica-data:/var/lib/postgresql/data
```

## 🔄 CI/CD Integration

### GitHub Actions

El despliegue se integra automáticamente con GitHub Actions:

- **Push a `develop`** → Despliegue automático a staging
- **Push a `main`** → Despliegue automático a producción
- **Pull Request** → Tests automáticos

### Variables de GitHub Secrets

```bash
# Configurar en GitHub Repository Settings > Secrets
PRODUCTION_HOST=tu-servidor.com
PRODUCTION_USER=deploy
PRODUCTION_SSH_KEY=tu-clave-ssh-privada
PRODUCTION_ENV_VARS=contenido-del-archivo-env.production
```

## 📚 Recursos Adicionales

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Nginx Documentation](https://nginx.org/en/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)

## 🆘 Soporte

Para problemas específicos:

1. Revisar logs: `docker-compose logs -f`
2. Verificar health checks: `curl http://localhost:5000/health`
3. Consultar documentación de CI/CD: `docs/CI_CD.md`
4. Crear issue en GitHub con logs y configuración 