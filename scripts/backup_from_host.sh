#!/bin/bash
# Script de Backup desde el Host
# Sistema POS O'Data v2.0.2-enterprise
# Este script debe ejecutarse desde el host, no desde el contenedor

BACKUP_DIR="./backups"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/pos_odata_backup_${TIMESTAMP}.dump"

# Crear directorio si no existe
mkdir -p "$BACKUP_DIR"

echo "========================================"
echo "BACKUP DE BASE DE DATOS"
echo "Sistema POS O'Data v2.0.2-enterprise"
echo "========================================"
echo ""

# Crear backup usando docker exec
echo "📦 Creando backup: $(basename $BACKUP_FILE)"
docker-compose -f docker-compose.production.yml exec -T postgres pg_dump -U pos_user -d pos_odata -F c -f /backups/backup_${TIMESTAMP}.dump

# Copiar backup al host
docker-compose -f docker-compose.production.yml cp postgres:/backups/backup_${TIMESTAMP}.dump "$BACKUP_FILE"

# Comprimir backup
echo "🗜️  Comprimiendo backup..."
gzip "$BACKUP_FILE"
BACKUP_FILE_GZ="${BACKUP_FILE}.gz"

# Obtener tamaño
FILE_SIZE=$(du -h "$BACKUP_FILE_GZ" | cut -f1)

echo "✅ Backup creado exitosamente: $(basename $BACKUP_FILE_GZ)"
echo "   Tamaño: $FILE_SIZE"
echo "   Ubicación: $BACKUP_FILE_GZ"
echo ""

# Limpiar backups antiguos
echo "🗑️  Limpiando backups antiguos (más de $RETENTION_DAYS días)..."
find "$BACKUP_DIR" -name "pos_odata_backup_*.dump.gz" -type f -mtime +$RETENTION_DAYS -delete
echo "✅ Limpieza completada"
echo ""

echo "========================================"
echo "BACKUP COMPLETADO"
echo "========================================"

