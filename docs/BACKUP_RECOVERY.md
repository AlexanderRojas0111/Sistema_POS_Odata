# 💾 Guía de Backup y Recuperación - Sistema POS O'data

## 📋 Resumen

El Sistema POS O'data incluye un sistema robusto de backup y recuperación diseñado para proteger los datos críticos del negocio y garantizar la continuidad operativa.

## 🔄 Estrategia de Backup

### Frecuencia y Retención

- **Backup Diario**: 02:00 UTC (automático)
- **Backup Manual**: Bajo demanda
- **Retención**: 30 días (configurable)
- **Formato**: SQL comprimido (.sql.gz)
- **Ubicación**: `./backups/`

### Tipos de Backup

1. **Backup Completo**: Esquema + datos + configuraciones
2. **Backup de Esquema**: Solo estructura de base de datos
3. **Backup de Datos**: Solo contenido de tablas
4. **Backup de Configuración**: Archivos de configuración

## 🛠️ Configuración

### Variables de Entorno

```env
# Backup Configuration
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE=0 2 * * *
BACKUP_COMPRESS=true
BACKUP_ENCRYPT=false
```

### Servicios Docker

**pos-odata-backup:**
- Imagen: postgres:15-alpine
- Función: Backup manual
- Frecuencia: Bajo demanda

**pos-odata-backup-cron:**
- Imagen: bitnami/cron:latest
- Función: Backup automático
- Frecuencia: Diario a las 02:00

## 📦 Procedimientos de Backup

### Backup Automático

El sistema ejecuta backup automático diariamente:

```bash
# Verificar estado del cron
docker compose -f docker-compose.production.yml ps backup-cron

# Ver logs del backup
docker compose -f docker-compose.production.yml logs backup-cron
```

### Backup Manual

**Ejecutar backup inmediato:**
```bash
# Backup completo
docker compose -f docker-compose.production.yml run --rm backup

# Ver archivos generados
ls -la backups/
```

**Backup con comando directo:**
```bash
# Backup personalizado
docker run --rm --network sistema_pos_odata_pos-network \
  -e PGPASSWORD=your_password \
  -e POSTGRES_USER=pos_user \
  -e POSTGRES_DB=pos_db_production \
  -v ${PWD}/backups:/backups \
  postgres:15-alpine sh -c "pg_dump -h db -p 5432 -U pos_user -d pos_db_production --verbose --clean --create --if-exists > /backups/backup_$(date +%Y%m%d_%H%M%S).sql && gzip /backups/backup_*.sql"
```

### Backup de Esquema

```bash
# Solo esquema
docker exec pos-odata-db pg_dump -U pos_user -d pos_db_production --schema-only > schema_backup.sql

# Solo datos
docker exec pos-odata-db pg_dump -U pos_user -d pos_db_production --data-only > data_backup.sql
```

## 🔄 Procedimientos de Recuperación

### Recuperación Completa

**Desde backup comprimido:**
```bash
# Descomprimir backup
gunzip backups/pos_db_backup_YYYYMMDD_HHMMSS.sql.gz

# Restaurar base de datos
docker exec -i pos-odata-db psql -U pos_user -d pos_db_production < backups/pos_db_backup_YYYYMMDD_HHMMSS.sql
```

**Desde backup directo:**
```bash
# Restaurar directamente
docker exec -i pos-odata-db psql -U pos_user -d pos_db_production < backups/backup_file.sql
```

### Recuperación Parcial

**Solo esquema:**
```bash
# Restaurar esquema
docker exec -i pos-odata-db psql -U pos_user -d pos_db_production < schema_backup.sql
```

**Solo datos:**
```bash
# Restaurar datos
docker exec -i pos_user -d pos_db_production < data_backup.sql
```

### Recuperación de Tabla Específica

```bash
# Backup de tabla específica
docker exec pos-odata-db pg_dump -U pos_user -d pos_db_production -t products > products_backup.sql

# Restaurar tabla específica
docker exec -i pos-odata-db psql -U pos_user -d pos_db_production < products_backup.sql
```

## 🔍 Verificación de Backups

### Verificar Integridad

```bash
# Verificar archivo comprimido
gunzip -t backups/pos_db_backup_YYYYMMDD_HHMMSS.sql.gz

# Verificar contenido
gunzip -c backups/pos_db_backup_YYYYMMDD_HHMMSS.sql.gz | head -20
```

### Verificar Tamaño

```bash
# Listar archivos de backup
ls -lh backups/

# Verificar espacio utilizado
du -sh backups/
```

### Verificar Fechas

```bash
# Ver fechas de modificación
ls -la backups/

# Verificar backups recientes
find backups/ -name "*.sql*" -mtime -1
```

## 🧹 Mantenimiento de Backups

### Limpieza Automática

El sistema incluye limpieza automática:

```bash
# Verificar configuración de retención
echo $BACKUP_RETENTION_DAYS

# Limpiar manualmente
find backups/ -name "*.sql*" -type f -mtime +30 -delete
```

### Rotación de Backups

```bash
# Mover backups antiguos
mkdir -p backups/archive
mv backups/pos_db_backup_*.sql.gz backups/archive/

# Comprimir backups antiguos
tar -czf backups/archive_$(date +%Y%m).tar.gz backups/archive/
```

## 🚨 Recuperación de Emergencia

### Procedimiento de Emergencia

1. **Detener servicios:**
```bash
docker compose -f docker-compose.production.yml down
```

2. **Restaurar base de datos:**
```bash
# Crear nueva base de datos
docker exec pos-odata-db createdb -U pos_user pos_db_production_new

# Restaurar desde backup
docker exec -i pos-odata-db psql -U pos_user -d pos_db_production_new < backups/latest_backup.sql
```

3. **Verificar restauración:**
```bash
# Verificar tablas
docker exec pos-odata-db psql -U pos_user -d pos_db_production_new -c "\dt"

# Verificar datos
docker exec pos-odata-db psql -U pos_user -d pos_db_production_new -c "SELECT COUNT(*) FROM products;"
```

4. **Reiniciar servicios:**
```bash
docker compose -f docker-compose.production.yml up -d
```

### Verificación Post-Recuperación

```bash
# Verificar estado de servicios
docker compose -f docker-compose.production.yml ps

# Verificar logs
docker compose -f docker-compose.production.yml logs app

# Probar API
curl http://localhost:5000/health
```

## 📊 Monitoreo de Backups

### Verificar Estado

```bash
# Ver logs de backup
docker compose -f docker-compose.production.yml logs backup-cron

# Verificar archivos recientes
ls -la backups/ | head -10
```

### Alertas

**Configurar alertas para:**
- Backup fallido
- Archivo de backup corrupto
- Espacio en disco insuficiente
- Backup no ejecutado en 24 horas

### Métricas

**Monitorear:**
- Tamaño de backups
- Tiempo de ejecución
- Frecuencia de ejecución
- Espacio en disco utilizado

## 🔐 Seguridad de Backups

### Encriptación

**Configurar encriptación:**
```env
BACKUP_ENCRYPT=true
BACKUP_ENCRYPT_PASSWORD=your_encryption_password
```

**Encriptar backup:**
```bash
# Encriptar archivo
openssl enc -aes-256-cbc -salt -in backup.sql -out backup.sql.enc -pass pass:password

# Desencriptar archivo
openssl enc -aes-256-cbc -d -in backup.sql.enc -out backup.sql -pass pass:password
```

### Almacenamiento Seguro

**Ubicaciones recomendadas:**
- Almacenamiento local cifrado
- Almacenamiento en la nube cifrado
- Múltiples ubicaciones geográficas

### Acceso

**Permisos de archivos:**
```bash
# Restringir acceso
chmod 600 backups/*.sql*
chown pos_user:pos_user backups/*.sql*
```

## 📋 Checklist de Backup

### Diario
- [ ] Verificar ejecución automática
- [ ] Verificar integridad del archivo
- [ ] Verificar tamaño del archivo
- [ ] Verificar fecha de creación

### Semanal
- [ ] Probar restauración de backup
- [ ] Verificar limpieza automática
- [ ] Verificar espacio en disco
- [ ] Revisar logs de backup

### Mensual
- [ ] Probar recuperación completa
- [ ] Verificar encriptación
- [ ] Actualizar documentación
- [ ] Revisar políticas de retención

## 🆘 Solución de Problemas

### Backup Fallido

**Causas comunes:**
- Espacio en disco insuficiente
- Permisos incorrectos
- Base de datos no disponible
- Contraseña incorrecta

**Soluciones:**
```bash
# Verificar espacio
df -h

# Verificar permisos
ls -la backups/

# Verificar base de datos
docker compose -f docker-compose.production.yml ps db

# Verificar logs
docker compose -f docker-compose.production.yml logs backup
```

### Restauración Fallida

**Causas comunes:**
- Archivo de backup corrupto
- Versión incompatible
- Espacio insuficiente
- Permisos incorrectos

**Soluciones:**
```bash
# Verificar integridad
gunzip -t backup.sql.gz

# Verificar versión
gunzip -c backup.sql.gz | head -10

# Verificar espacio
df -h

# Verificar permisos
ls -la backup.sql
```

---

**Última actualización**: 23 de septiembre de 2025
**Versión**: 2.0.0
