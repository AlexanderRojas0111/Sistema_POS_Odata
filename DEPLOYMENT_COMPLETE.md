# 🚀 **Sistema POS Odata - Guía Completa de Despliegue**

## 📋 **Tabla de Contenidos**

1. [Requisitos del Sistema](#requisitos-del-sistema)
2. [Preparación del Entorno](#preparación-del-entorno)
3. [Configuración de CI/CD](#configuración-de-cicd)
4. [Despliegue Paso a Paso](#despliegue-paso-a-paso)
5. [Configuración de Monitoreo](#configuración-de-monitoreo)
6. [Configuración de Seguridad](#configuración-de-seguridad)
7. [Pruebas y Validación](#pruebas-y-validación)
8. [Mantenimiento y Operaciones](#mantenimiento-y-operaciones)
9. [Troubleshooting](#troubleshooting)
10. [Escalabilidad y Mejoras](#escalabilidad-y-mejoras)

---

## 🖥️ **Requisitos del Sistema**

### **Hardware Mínimo**
- **Servidor Principal**: 2 vCPU, 4 GB RAM, 30 GB SSD
- **Base de Datos**: 2 vCPU, 8 GB RAM, SSD con IOPS estables
- **Cache Redis**: 1 vCPU, 2 GB RAM
- **Almacenamiento**: 100 GB total (incluyendo backups)

### **Hardware Recomendado**
- **Servidor Principal**: 4 vCPU, 16 GB RAM, 100 GB SSD NVMe
- **Base de Datos**: 4 vCPU, 16 GB RAM, SSD NVMe separado
- **Cache Redis**: 2 vCPU, 4 GB RAM
- **Almacenamiento**: 500 GB total con RAID 1

### **Software Requerido**
- **Sistema Operativo**: Ubuntu 22.04 LTS o CentOS 8+
- **Docker**: 24.0+
- **Docker Compose**: v2.20+
- **Python**: 3.13+
- **Node.js**: 20.x (para build del frontend)
- **Git**: 2.40+

### **Requisitos de Red**
- **Ancho de Banda**: Mínimo 100 Mbps, recomendado 1 Gbps
- **Puertos**: 80 (HTTP), 443 (HTTPS), 22 (SSH)
- **DNS**: Dominio configurado (ej: `pos.odata.com`)
- **Firewall**: Configurado para permitir tráfico web

---

## 🛠️ **Preparación del Entorno**

### **1. Configuración del Servidor**

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar dependencias básicas
sudo apt install -y curl wget git unzip software-properties-common

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Instalar Node.js para build del frontend
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verificar instalaciones
docker --version
docker-compose --version
node --version
npm --version
```

### **2. Configuración de Directorios**

```bash
# Crear estructura de directorios
sudo mkdir -p /opt/pos-odata/{logs,uploads,backups,ssl}
sudo mkdir -p /opt/pos-odata/monitoring/{prometheus,grafana,alertmanager}

# Configurar permisos
sudo chown -R $USER:$USER /opt/pos-odata
sudo chmod -R 755 /opt/pos-odata
sudo chmod 700 /opt/pos-odata/ssl
```

### **3. Clonar el Repositorio**

```bash
cd /opt
git clone https://github.com/odata/sistema-pos-odata.git pos-odata
cd pos-odata

# Verificar estructura
ls -la
```

---

## 🔄 **Configuración de CI/CD**

### **1. GitHub Actions**

El workflow ya está configurado en `.github/workflows/ci-cd.yml`. Solo necesitas configurar los secrets:

```bash
# En GitHub Repository > Settings > Secrets and variables > Actions
STAGING_HOST=tu-servidor-staging
PRODUCTION_HOST=tu-servidor-produccion
SSH_USER=tu-usuario
SSH_KEY=tu-clave-ssh-privada
SSH_PORT=22
SLACK_WEBHOOK_URL=tu-webhook-slack
```

### **2. Jenkins (Alternativa)**

Si prefieres Jenkins, el `Jenkinsfile` ya está configurado. Configura las credenciales:

```bash
# En Jenkins > Manage Jenkins > Credentials
docker-registry-credentials
ssh-credentials
slack-webhook
github-credentials
```

### **3. Configuración de Entornos**

```bash
# Copiar archivos de configuración
cp env.example env.production
cp env.example env.staging

# Editar configuración de producción
nano env.production
```

**Variables críticas para producción:**
```bash
# Base de datos
DB_PASSWORD=tu-password-seguro
DB_HOST=db
DB_PORT=5432
DB_NAME=pos_odata_prod

# Redis
REDIS_PASSWORD=tu-password-redis
REDIS_HOST=redis
REDIS_PORT=6379

# JWT y seguridad
SECRET_KEY=tu-secret-key-muy-largo
JWT_SECRET_KEY=tu-jwt-secret-key-muy-largo

# Dominio
DOMAIN=pos.odata.com
CORS_ORIGINS=https://pos.odata.com,https://www.pos.odata.com
```

---

## 🚀 **Despliegue Paso a Paso**

### **1. Despliegue Inicial**

```bash
# Navegar al directorio del proyecto
cd /opt/pos-odata

# Generar certificados SSL
sudo ./scripts/generate_ssl_certificates.sh --letsencrypt

# Construir y desplegar
docker-compose -f docker-compose.production.yml up -d --build

# Verificar estado de los servicios
docker-compose -f docker-compose.production.yml ps
```

### **2. Verificación del Despliegue**

```bash
# Health checks
curl -f https://pos.odata.com/health
curl -f https://pos.odata.com/api/v1/health

# Verificar logs
docker-compose -f docker-compose.production.yml logs -f app
docker-compose -f docker-compose.production.yml logs -f nginx

# Verificar métricas
curl -f http://localhost:9090/-/healthy  # Prometheus
curl -f http://localhost:3000/api/health # Grafana
```

### **3. Configuración de Base de Datos**

```bash
# Ejecutar migraciones
docker-compose -f docker-compose.production.yml exec app flask db upgrade

# Cargar datos iniciales (si es necesario)
docker-compose -f docker-compose.production.yml exec app python scripts/init_db.py

# Verificar conexión
docker-compose -f docker-compose.production.yml exec app python scripts/health_check.py
```

---

## 📊 **Configuración de Monitoreo**

### **1. Prometheus**

```bash
# Verificar configuración
docker-compose -f docker-compose.production.yml exec prometheus promtool check config /etc/prometheus/prometheus.yml

# Verificar targets
curl http://localhost:9090/api/v1/targets

# Verificar reglas de alertas
curl http://localhost:9090/api/v1/rules
```

### **2. Grafana**

```bash
# Acceder a Grafana
# URL: http://localhost:3000
# Usuario: admin
# Password: admin (cambiar en primer login)

# Importar dashboards
# 1. Sistema POS Odata - Overview
# 2. Sistema POS Odata - Métricas de Negocio

# Configurar fuentes de datos
# - Prometheus: http://prometheus:9090
```

### **3. Alertas**

```bash
# Verificar estado de alertas
curl http://localhost:9090/api/v1/alerts

# Configurar notificaciones (Slack, email, etc.)
# En Grafana: Alerting > Notification channels
```

---

## 🔒 **Configuración de Seguridad**

### **1. Firewall**

```bash
# Configurar UFW
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Verificar estado
sudo ufw status verbose
```

### **2. SSL/TLS**

```bash
# Verificar certificados
sudo openssl x509 -in /etc/nginx/ssl/pos.odata.com.crt -text -noout

# Verificar renovación automática
sudo crontab -l | grep renew-ssl-certs

# Probar configuración SSL
curl -I https://pos.odata.com
```

### **3. Seguridad de la Aplicación**

```bash
# Verificar headers de seguridad
curl -I https://pos.odata.com | grep -E "(Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection)"

# Verificar rate limiting
# Probar múltiples requests rápidos
for i in {1..20}; do curl -s https://pos.odata.com/api/v1/health; done
```

---

## 🧪 **Pruebas y Validación**

### **1. Pruebas de Funcionalidad**

```bash
# Pruebas de API
curl -X POST https://pos.odata.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Pruebas de frontend
# Abrir https://pos.odata.com en navegador
# Verificar login, navegación, funcionalidades básicas
```

### **2. Pruebas de Rendimiento**

```bash
# Instalar k6
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6

# Ejecutar prueba de carga
k6 run scripts/load-test.js
```

### **3. Pruebas de Seguridad**

```bash
# Escanear vulnerabilidades
docker run --rm -v $(pwd):/app aquasec/trivy fs /app

# Verificar dependencias
pip-audit -r requirements.txt
npm audit --audit-level=high
```

---

## 🔧 **Mantenimiento y Operaciones**

### **1. Backups Automáticos**

```bash
# Verificar script de backup
./scripts/backup.sh

# Configurar cron para backups diarios
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/pos-odata/scripts/backup.sh") | crontab -

# Verificar backups
ls -la backups/
```

### **2. Logs y Monitoreo**

```bash
# Ver logs en tiempo real
docker-compose -f docker-compose.production.yml logs -f

# Rotar logs
sudo logrotate -f /etc/logrotate.d/pos-odata

# Verificar espacio en disco
df -h
du -sh /opt/pos-odata/logs/*
```

### **3. Actualizaciones**

```bash
# Actualizar código
git pull origin main

# Reconstruir y desplegar
docker-compose -f docker-compose.production.yml down
docker-compose -f docker-compose.production.yml up -d --build

# Verificar actualización
docker-compose -f docker-compose.production.yml ps
```

---

## 🚨 **Troubleshooting**

### **1. Problemas Comunes**

```bash
# Servicio no inicia
docker-compose -f docker-compose.production.yml logs app

# Base de datos no conecta
docker-compose -f docker-compose.production.yml exec app python -c "from app.core.database import db; print(db.engine.execute('SELECT 1').scalar())"

# Redis no responde
docker-compose -f docker-compose.production.yml exec redis redis-cli ping

# Nginx no sirve
sudo nginx -t
sudo systemctl status nginx
```

### **2. Recuperación de Errores**

```bash
# Rollback a versión anterior
docker-compose -f docker-compose.production.yml down
git checkout HEAD~1
docker-compose -f docker-compose.production.yml up -d

# Restaurar base de datos
docker-compose -f docker-compose.production.yml exec db psql -U postgres -d pos_odata_prod < backup.sql

# Reiniciar servicios
docker-compose -f docker-compose.production.yml restart
```

### **3. Logs de Error**

```bash
# Ver errores de aplicación
tail -f /opt/pos-odata/logs/app.log | grep ERROR

# Ver errores de Nginx
sudo tail -f /var/log/nginx/pos.odata.com.error.log

# Ver errores de base de datos
docker-compose -f docker-compose.production.yml logs db | grep ERROR
```

---

## 📈 **Escalabilidad y Mejoras**

### **1. Escalado Horizontal**

```bash
# Escalar backend
docker-compose -f docker-compose.production.yml up -d --scale app=3

# Configurar load balancer
# Editar nginx/production.conf para usar upstream con múltiples instancias
```

### **2. Optimizaciones de Rendimiento**

```bash
# Configurar cache Redis
docker-compose -f docker-compose.production.yml exec redis redis-cli CONFIG SET maxmemory-policy allkeys-lru

# Optimizar base de datos
docker-compose -f docker-compose.production.yml exec db psql -U postgres -c "ALTER SYSTEM SET shared_buffers = '256MB';"
docker-compose -f docker-compose.production.yml exec db psql -U postgres -c "SELECT pg_reload_conf();"
```

### **3. Monitoreo Avanzado**

```bash
# Configurar alertas personalizadas
# Editar monitoring/prometheus/alerts/pos-alerts.yml

# Configurar dashboards adicionales
# Crear nuevos dashboards en Grafana para métricas específicas
```

---

## 📚 **Recursos Adicionales**

### **Documentación**
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Prometheus Configuration](https://prometheus.io/docs/prometheus/latest/configuration/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Nginx Configuration](https://nginx.org/en/docs/)

### **Herramientas Útiles**
- **Monitoreo**: Prometheus, Grafana, Alertmanager
- **Logs**: ELK Stack, Loki
- **Backup**: pg_dump, rsync, tar
- **Seguridad**: Trivy, Bandit, Safety

### **Contactos de Soporte**
- **DevOps**: devops@odata.com
- **Desarrollo**: dev@odata.com
- **Soporte**: support@odata.com

---

## ✅ **Checklist de Despliegue Exitoso**

- [ ] Servidor configurado con requisitos mínimos
- [ ] Docker y Docker Compose instalados
- [ ] Repositorio clonado y configurado
- [ ] Variables de entorno configuradas
- [ ] Certificados SSL generados
- [ ] Servicios desplegados y funcionando
- [ ] Base de datos migrada y poblada
- [ ] Monitoreo configurado (Prometheus, Grafana)
- [ ] Alertas configuradas y funcionando
- [ ] Backups automáticos configurados
- [ ] Firewall y seguridad configurados
- [ ] Pruebas de funcionalidad exitosas
- [ ] Pruebas de rendimiento exitosas
- [ ] Documentación actualizada
- [ ] Equipo capacitado en operaciones

---

**🎉 ¡Felicidades! Tu sistema POS Odata está desplegado y funcionando en producción.**

**📞 Para soporte técnico o preguntas, contacta al equipo de DevOps.**
