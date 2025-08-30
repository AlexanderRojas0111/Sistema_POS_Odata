# 🏢 Configuración para Producción Empresarial

## 🔧 Variables de Entorno de Producción

### 1. Copiar y editar archivo de configuración
```bash
cp env.example env.production
nano env.production
```

### 2. Configurar variables críticas:
```bash
# === SEGURIDAD (CAMBIAR OBLIGATORIO) ===
SECRET_KEY=TU_CLAVE_SECRETA_UNICA_64_CARACTERES
JWT_SECRET_KEY=TU_JWT_SECRET_MUY_LARGO_Y_SEGURO
DB_PASSWORD=TU_PASSWORD_DB_SUPER_SEGURO
REDIS_PASSWORD=TU_PASSWORD_REDIS_SEGURO

# === DOMINIO ===
CORS_ORIGINS=https://pos.tu-empresa.com,https://api.tu-empresa.com
FLASK_RUN_HOST=0.0.0.0

# === BASE DE DATOS ===
DATABASE_URL=postgresql://pos_user:${DB_PASSWORD}@db:5432/pos_db_production
POSTGRES_DB=pos_db_production
POSTGRES_USER=pos_user

# === CONFIGURACIÓN DE PRODUCCIÓN ===
FLASK_ENV=production
FLASK_DEBUG=False
LOG_LEVEL=WARNING

# === RATE LIMITING ===
RATELIMIT_ENABLED=true
RATELIMIT_DEFAULT=1000 per day;100 per hour;20 per minute

# === SEGURIDAD ADICIONAL ===
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Strict
```

## 🚀 Comandos de Despliegue

### 1. Preparar directorios
```bash
mkdir -p logs uploads backups data/ssl
sudo chown -R $USER:$USER logs uploads backups
```

### 2. Generar certificados SSL (si usas Let's Encrypt)
```bash
# Copiar certificados de Let's Encrypt
sudo cp /etc/letsencrypt/live/pos.tu-empresa.com/fullchain.pem data/ssl/cert.pem
sudo cp /etc/letsencrypt/live/pos.tu-empresa.com/privkey.pem data/ssl/key.pem
sudo chown $USER:$USER data/ssl/*
```

### 3. Desplegar sistema
```bash
# Despliegue completo
docker-compose -f docker-compose.production.yml up -d --build

# Verificar estado
docker-compose -f docker-compose.production.yml ps

# Ver logs
docker-compose -f docker-compose.production.yml logs -f
```

### 4. Configurar Nginx (Proxy Reverso)
```bash
# Instalar Nginx en el servidor
sudo apt install nginx

# Configurar virtual host
sudo nano /etc/nginx/sites-available/pos-odata
```

**Configuración Nginx:**
```nginx
server {
    listen 80;
    server_name pos.tu-empresa.com api.tu-empresa.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name pos.tu-empresa.com api.tu-empresa.com;

    ssl_certificate /path/to/ssl/cert.pem;
    ssl_certificate_key /path/to/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # API Backend
    location /api/ {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Health checks
    location /health {
        proxy_pass http://localhost:5000;
    }

    # Frontend (cuando esté implementado)
    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
    }
}
```

```bash
# Activar configuración
sudo ln -s /etc/nginx/sites-available/pos-odata /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## 🔐 Configuración de Seguridad

### 1. Firewall avanzado
```bash
# Configurar UFW más restrictivo
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH (solo tu IP)
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. Fail2Ban (protección contra ataques)
```bash
sudo apt install fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 3. Configurar backups automáticos
```bash
# Crear script de backup
chmod +x scripts/backup.sh

# Configurar cron para backups diarios
crontab -e
# Agregar: 0 2 * * * /path/to/Sistema_POS_Odata/scripts/backup.sh
```

## 📊 Monitoreo y Alertas

### 1. Configurar Grafana (opcional)
```bash
# Acceder a Grafana
# URL: https://pos.tu-empresa.com:3000
# Usuario: admin
# Password: (configurado en env.production)
```

### 2. Configurar alertas por email
```bash
# Editar env.production
ALERT_EMAIL=admin@tu-empresa.com
SMTP_SERVER=smtp.tu-empresa.com
SMTP_PORT=587
SMTP_USER=alertas@tu-empresa.com
SMTP_PASSWORD=password_smtp
```

## 🧪 Validación Post-Despliegue

### 1. Tests de funcionalidad
```bash
# Health check
curl https://api.tu-empresa.com/health

# Test de API
curl -X POST https://api.tu-empresa.com/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 2. Tests de carga (opcional)
```bash
# Instalar herramientas de testing
pip install locust

# Ejecutar test de carga
locust -f tests/test_performance.py --host=https://api.tu-empresa.com
```

## 📋 Checklist de Producción

### ✅ Pre-Despliegue
- [ ] Servidor configurado con requisitos mínimos
- [ ] Docker y Docker Compose instalados
- [ ] Dominio registrado y DNS configurado
- [ ] Certificados SSL obtenidos
- [ ] Variables de entorno configuradas
- [ ] Firewall configurado

### ✅ Despliegue
- [ ] Código clonado desde GitHub
- [ ] Servicios desplegados con Docker Compose
- [ ] Nginx configurado como proxy reverso
- [ ] SSL/TLS funcionando
- [ ] Health checks pasando

### ✅ Post-Despliegue
- [ ] Tests de funcionalidad ejecutados
- [ ] Monitoreo configurado
- [ ] Backups automáticos configurados
- [ ] Alertas configuradas
- [ ] Documentación actualizada

## 🎯 URLs de Acceso Final

- **🌐 Frontend**: `https://pos.tu-empresa.com`
- **🔌 API**: `https://api.tu-empresa.com/api/v1/`
- **❤️ Health**: `https://api.tu-empresa.com/health`
- **📊 Monitoreo**: `https://pos.tu-empresa.com:3000` (Grafana)

---

**🎉 ¡Sistema POS Odata listo para operar en producción empresarial!** 🎉

