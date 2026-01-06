# 📋 Guía Post-Despliegue - Sistema POS O'Data

## ✅ Tareas Completadas

### **1. Scripts Creados**
- ✅ `scripts/change_admin_password.py` - Cambio seguro de contraseña
- ✅ `scripts/validate_endpoints.py` - Validación de endpoints
- ✅ `scripts/backup_database.py` - Backups automáticos
- ✅ `scripts/review_logs.py` - Revisión de logs

### **2. Validaciones Realizadas**
- ✅ Health checks funcionando correctamente
- ✅ Todos los servicios healthy
- ✅ Base de datos operativa (48 tablas, 65 foreign keys)
- ✅ Redis configurado con autenticación

---

## 🔐 Paso 1: Cambiar Contraseña del Administrador

### **Opción A: Usando el Script (Recomendado)**

```bash
docker-compose -f docker-compose.production.yml exec pos-app python scripts/change_admin_password.py
```

El script solicitará:
1. Nueva contraseña (mínimo 6 caracteres)
2. Confirmación de contraseña

### **Opción B: Manualmente (SQL)**

```bash
# Conectarse a PostgreSQL
docker-compose -f docker-compose.production.yml exec postgres psql -U pos_user -d pos_odata

# Cambiar contraseña (usar el hash bcrypt generado)
# Nota: Es mejor usar el script que genera el hash correctamente
```

### **Opción C: Usando la API**

```bash
# Primero hacer login con credenciales actuales
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Luego usar el endpoint de cambio de contraseña (si está disponible)
```

---

## 🔍 Paso 2: Validar Endpoints Principales

### **Health Checks**

```bash
# Health check básico
curl http://localhost:8000/api/v1/health

# Health check detallado
curl http://localhost:8000/api/v1/health/detailed

# Métricas
curl http://localhost:8000/api/v1/health/metrics
```

### **Endpoints de Autenticación**

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "TU_CONTRASEÑA"}'
```

### **Endpoints Principales**

```bash
# Productos
curl http://localhost:8000/api/v1/products

# Usuarios (requiere autenticación)
curl http://localhost:8000/api/v1/users \
  -H "Authorization: Bearer TU_TOKEN"

# Ventas (requiere autenticación)
curl http://localhost:8000/api/v1/sales \
  -H "Authorization: Bearer TU_TOKEN"
```

### **Usando el Script de Validación**

```bash
docker-compose -f docker-compose.production.yml exec pos-app python scripts/validate_endpoints.py
```

---

## 💾 Paso 3: Configurar Backups Automáticos

### **Backup Manual**

```bash
# Crear backup
docker-compose -f docker-compose.production.yml exec postgres pg_dump -U pos_user -d pos_odata -F c -f /backups/backup_$(date +%Y%m%d_%H%M%S).dump

# Listar backups
docker-compose -f docker-compose.production.yml exec postgres ls -lh /backups/
```

### **Backup con el Script**

```bash
# Crear backup
docker-compose -f docker-compose.production.yml exec pos-app python scripts/backup_database.py

# Listar backups
docker-compose -f docker-compose.production.yml exec pos-app python scripts/backup_database.py --list
```

### **Configurar Backups Automáticos**

#### **Opción 1: Cron en el Contenedor**

```bash
# Entrar al contenedor
docker-compose -f docker-compose.production.yml exec pos-app bash

# Editar crontab
crontab -e

# Agregar línea (backup diario a las 2:00 AM)
0 2 * * * cd /app && python scripts/backup_database.py --backup-dir /app/backups --retention-days 30 >> /app/logs/backup.log 2>&1
```

#### **Opción 2: Cron en el Host (Recomendado)**

Crear script en el host: `backup_daily.sh`

```bash
#!/bin/bash
cd /ruta/al/proyecto
docker-compose -f docker-compose.production.yml exec -T postgres pg_dump -U pos_user -d pos_odata -F c -f /backups/backup_$(date +%Y%m%d_%H%M%S).dump
```

Agregar a crontab del host:
```bash
0 2 * * * /ruta/al/backup_daily.sh
```

#### **Opción 3: Usando Docker Compose con Cron**

Agregar servicio en `docker-compose.production.yml`:
```yaml
  backup:
    image: sistema_pos_odata-pos-app
    command: python scripts/backup_database.py
    volumes:
      - ./backups:/app/backups
    depends_on:
      - postgres
    restart: "no"
```

---

## 📊 Paso 4: Revisar Logs

### **Ver Logs en Tiempo Real**

```bash
# Logs de la aplicación
docker-compose -f docker-compose.production.yml logs -f pos-app

# Logs de todos los servicios
docker-compose -f docker-compose.production.yml logs -f

# Logs de PostgreSQL
docker-compose -f docker-compose.production.yml logs -f postgres

# Logs de Redis
docker-compose -f docker-compose.production.yml logs -f redis
```

### **Ver Últimos Logs**

```bash
# Últimas 50 líneas
docker-compose -f docker-compose.production.yml logs --tail=50 pos-app

# Buscar errores
docker-compose -f docker-compose.production.yml logs pos-app | grep ERROR

# Buscar advertencias
docker-compose -f docker-compose.production.yml logs pos-app | grep WARNING
```

### **Usando el Script de Revisión**

```bash
docker-compose -f docker-compose.production.yml exec pos-app python scripts/review_logs.py
```

---

## 📋 Checklist Final

### **Críticas (Hacer Ahora)**
- [ ] Cambiar contraseña del administrador
- [ ] Verificar que health checks responden
- [ ] Validar login con nueva contraseña

### **Importantes (Próximas 24 horas)**
- [ ] Configurar backups automáticos
- [ ] Probar restauración de backup
- [ ] Revisar logs para errores
- [ ] Validar endpoints principales

### **Recomendadas (Próxima semana)**
- [ ] Configurar monitoreo avanzado
- [ ] Establecer alertas
- [ ] Documentar procedimientos de recuperación
- [ ] Revisar y optimizar configuración

---

## 🔧 Comandos Útiles

```bash
# Estado de servicios
docker-compose -f docker-compose.production.yml ps

# Reiniciar servicios
docker-compose -f docker-compose.production.yml restart

# Ver uso de recursos
docker stats

# Entrar a contenedor
docker-compose -f docker-compose.production.yml exec pos-app bash

# Ver variables de entorno
docker-compose -f docker-compose.production.yml exec pos-app env | grep -E "DATABASE|REDIS|SECRET"

# Verificar conexión a base de datos
docker-compose -f docker-compose.production.yml exec postgres psql -U pos_user -d pos_odata -c "SELECT version();"

# Verificar conexión a Redis
docker-compose -f docker-compose.production.yml exec redis redis-cli -a TU_PASSWORD ping
```

---

## ⚠️ Notas Importantes

1. **Contraseña del Administrador**: Cambiar inmediatamente después del despliegue
2. **Backups**: Configurar backups automáticos y probar restauración
3. **Logs**: Revisar regularmente para detectar problemas
4. **Monitoreo**: Configurar alertas para servicios críticos
5. **Seguridad**: Revisar configuración de firewall y acceso

---

*Sistema POS O'Data v2.0.2-enterprise - Guía Post-Despliegue*

