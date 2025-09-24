# 🚀 Guía de Despliegue - Sistema POS O'data v2.0.0

## 📋 Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Prerrequisitos](#prerrequisitos)
3. [Despliegue Local](#despliegue-local)
4. [Despliegue con Docker](#despliegue-con-docker)
5. [Despliegue en Producción](#despliegue-en-producción)
6. [Configuración de Seguridad](#configuración-de-seguridad)
7. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Resumen Ejecutivo

El Sistema POS O'data v2.0.0 es una aplicación web moderna con funcionalidades de IA que requiere una configuración cuidadosa para un despliegue exitoso. Esta guía cubre todos los escenarios de despliegue desde desarrollo local hasta producción empresarial.

### ✨ Características del Sistema
- **Backend**: Flask 3.1.1 con Python 3.11+
- **Base de Datos**: PostgreSQL/SQLite
- **Cache**: Redis
- **IA**: scikit-learn para búsqueda semántica
- **Frontend**: React 18.2.0
- **Containerización**: Docker y Docker Compose

---

## 📋 Prerrequisitos

### 🖥️ Requisitos del Sistema

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| **CPU** | 2 cores | 4+ cores |
| **RAM** | 4 GB | 8+ GB |
| **Almacenamiento** | 10 GB | 20+ GB SSD |
| **SO** | Linux/Windows/macOS | Linux Ubuntu 20.04+ |

### 🔧 Software Requerido

```bash
# Verificar versiones
python --version    # 3.11+
node --version      # 18+
docker --version    # 20+
git --version       # 2.30+
```

---

## 🏠 Despliegue Local

### 1️⃣ Clonar y Configurar

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/sistema-pos-odata.git
cd sistema-pos-odata

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

### 2️⃣ Configurar Entorno

```bash
# Generar archivo .env seguro
python scripts/setup_secure_env.py development

# Editar configuraciones si es necesario
nano .env
```

### 3️⃣ Inicializar Base de Datos

```bash
# Ejecutar migraciones
python scripts/init_db.py

# Cargar datos de ejemplo (opcional)
python scripts/load_sample_data.py
```

### 4️⃣ Ejecutar Aplicación

```bash
# Iniciar servidor backend
python run_server.py

# En otra terminal, iniciar frontend
cd frontend
npm install
npm start
```

### 5️⃣ Verificar Instalación

```bash
# Ejecutar validación completa
python scripts/validate_system.py

# Acceder a la aplicación
# Backend: http://localhost:5000
# Frontend: http://localhost:3000
```

---

## 🐳 Despliegue con Docker

### 🚀 Despliegue Rápido

```bash
# Construir y ejecutar todos los servicios
docker-compose up -d

# Verificar servicios
docker-compose ps

# Ver logs
docker-compose logs -f app
```

### 🔧 Configuración Avanzada

```bash
# Usar archivo de producción
docker-compose -f docker-compose.production.yml up -d

# Escalar servicios
docker-compose up -d --scale app=3 --scale worker=2

# Ejecutar migraciones
docker-compose exec app python scripts/init_db.py
```

### 📊 Servicios Incluidos

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **app** | 5000 | Aplicación Flask |
| **frontend** | 3000 | React UI |
| **db** | 5432 | PostgreSQL |
| **redis** | 6379 | Cache/Sessions |
| **prometheus** | 9090 | Métricas |
| **grafana** | 3001 | Dashboards |

---

## 🏭 Despliegue en Producción

### ☁️ AWS Deployment

```bash
# 1. Configurar AWS CLI
aws configure

# 2. Crear infraestructura
terraform init
terraform plan
terraform apply

# 3. Desplegar aplicación
./scripts/deploy_aws.sh
```

### 🔵 Azure Deployment

```bash
# 1. Login Azure
az login

# 2. Crear recursos
az group create --name pos-odata-rg --location eastus
az container create --resource-group pos-odata-rg --file azure-container.yml

# 3. Configurar dominio
az network dns record-set a add-record --resource-group pos-odata-rg --zone-name yourdomain.com --record-set-name pos --ipv4-address YOUR_IP
```

### 🟢 Google Cloud Deployment

```bash
# 1. Configurar GCloud
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 2. Desplegar en Cloud Run
gcloud run deploy pos-odata --source . --platform managed --region us-central1 --allow-unauthenticated

# 3. Configurar base de datos
gcloud sql instances create pos-odata-db --database-version=POSTGRES_13 --tier=db-f1-micro --region=us-central1
```

---

## 🔒 Configuración de Seguridad

### 🔑 Variables de Entorno de Producción

```bash
# Generar claves seguras
python scripts/setup_secure_env.py production

# Variables críticas a configurar:
SECRET_KEY=your-ultra-secure-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/db
CORS_ORIGINS=https://yourdomain.com
```

### 🛡️ Checklist de Seguridad

- [ ] ✅ Claves secretas únicas y seguras
- [ ] ✅ HTTPS habilitado con certificados válidos
- [ ] ✅ CORS configurado con dominios específicos
- [ ] ✅ Rate limiting habilitado
- [ ] ✅ Firewall configurado
- [ ] ✅ Backups automáticos configurados
- [ ] ✅ Monitoreo de seguridad activo
- [ ] ✅ Logs de auditoría habilitados

### 🔍 Auditoría de Seguridad

```bash
# Ejecutar auditoría completa
python scripts/security_audit.py

# Instalar herramientas adicionales
pip install safety bandit
safety check
bandit -r app/
```

---

## 📊 Monitoreo y Mantenimiento

### 📈 Métricas Clave

| Métrica | Umbral | Acción |
|---------|---------|---------|
| **CPU Usage** | >80% | Escalar horizontalmente |
| **Memory Usage** | >85% | Investigar memory leaks |
| **Response Time** | >2s | Optimizar queries |
| **Error Rate** | >1% | Investigar logs |
| **Disk Usage** | >90% | Limpiar logs/backups |

### 🔧 Comandos de Mantenimiento

```bash
# Backup base de datos
python scripts/backup_database.py

# Limpiar logs antiguos
python scripts/cleanup_logs.py

# Actualizar dependencias
pip-review --auto

# Verificar salud del sistema
python scripts/health_check.py
```

### 📊 Dashboard de Monitoreo

Acceder a Grafana: `http://localhost:3001`
- Usuario: admin
- Contraseña: admin123

Dashboards disponibles:
- **Sistema General**: CPU, RAM, Disk
- **Aplicación**: Response time, Error rate
- **Base de Datos**: Connections, Queries
- **IA**: Embeddings, Search performance

---

## 🚨 Troubleshooting

### ❌ Problemas Comunes

#### 🔴 Error: "Port 5000 already in use"
```bash
# Encontrar proceso usando el puerto
lsof -i :5000
# Matar proceso
kill -9 PID
```

#### 🔴 Error: "Database connection failed"
```bash
# Verificar PostgreSQL
sudo systemctl status postgresql
# Reiniciar servicio
sudo systemctl restart postgresql
```

#### 🔴 Error: "Redis connection failed"
```bash
# Verificar Redis
redis-cli ping
# Reiniciar Redis
sudo systemctl restart redis
```

#### 🔴 Error: "Import Error: No module named 'sklearn'"
```bash
# Reinstalar scikit-learn
pip uninstall scikit-learn
pip install scikit-learn==1.7.1
```

### 🔍 Logs de Diagnóstico

```bash
# Ver logs de aplicación
tail -f logs/app.log

# Logs de Docker
docker-compose logs -f app

# Logs del sistema
journalctl -u pos-odata-app -f
```

### 📞 Soporte

- **Documentación**: [docs/](docs/)
- **Issues**: GitHub Issues
- **Email**: soporte@pos-odata.com
- **Chat**: Discord/Slack

---

## ✅ Checklist de Despliegue

### 🏠 Desarrollo Local
- [ ] Python 3.11+ instalado
- [ ] Dependencias instaladas
- [ ] .env configurado
- [ ] Base de datos inicializada
- [ ] Servidor ejecutándose
- [ ] Tests pasando

### 🐳 Docker
- [ ] Docker y Docker Compose instalados
- [ ] docker-compose.yml configurado
- [ ] Servicios ejecutándose
- [ ] Health checks pasando
- [ ] Volúmenes persistentes configurados

### 🏭 Producción
- [ ] Infraestructura provisionada
- [ ] DNS configurado
- [ ] SSL/TLS habilitado
- [ ] Monitoreo configurado
- [ ] Backups automatizados
- [ ] Alertas configuradas
- [ ] Documentación actualizada

---

## 🎯 Próximos Pasos

1. **Configurar CI/CD**: GitHub Actions, Jenkins
2. **Implementar Blue/Green Deployment**
3. **Configurar Auto-scaling**
4. **Implementar Disaster Recovery**
5. **Optimizar Performance**
6. **Seguridad Avanzada**: WAF, DDoS protection

---

<div align="center">

**🚀 ¡Sistema POS O'data listo para producción! 🚀**

</div>
