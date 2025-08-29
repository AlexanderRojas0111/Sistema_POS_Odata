#!/bin/bash

# Script de Backup Automático para Sistema POS Odata
# Este script debe ejecutarse como cron job para backups automáticos

set -e

# Configuración
BACKUP_DIR="/backups"
DB_HOST="db"
DB_PORT="5432"
DB_NAME="pos_db_production"
DB_USER="pos_user"
DB_PASSWORD="${DB_PASSWORD}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"
COMPRESS=true
ENCRYPT=false
ENCRYPT_PASSWORD=""

# Crear directorio de backup si no existe
mkdir -p "$BACKUP_DIR"

# Función de logging
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Función de limpieza de backups antiguos
cleanup_old_backups() {
    log "Limpiando backups antiguos (más de $RETENTION_DAYS días)..."
    find "$BACKUP_DIR" -name "*.sql*" -type f -mtime +$RETENTION_DAYS -delete
    log "Limpieza completada"
}

# Función de backup de base de datos
backup_database() {
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="$BACKUP_DIR/pos_db_backup_$timestamp.sql"
    
    log "Iniciando backup de base de datos..."
    log "Archivo de destino: $backup_file"
    
    # Crear backup usando pg_dump
    PGPASSWORD="$DB_PASSWORD" pg_dump \
        -h "$DB_HOST" \
        -p "$DB_PORT" \
        -U "$DB_USER" \
        -d "$DB_NAME" \
        --verbose \
        --clean \
        --create \
        --if-exists \
        --no-password \
        > "$backup_file"
    
    if [ $? -eq 0 ]; then
        log "Backup de base de datos completado exitosamente"
        
        # Comprimir backup si está habilitado
        if [ "$COMPRESS" = true ]; then
            log "Comprimiendo backup..."
            gzip "$backup_file"
            backup_file="$backup_file.gz"
            log "Backup comprimido: $backup_file"
        fi
        
        # Encriptar backup si está habilitado
        if [ "$ENCRYPT" = true ] && [ -n "$ENCRYPT_PASSWORD" ]; then
            log "Encriptando backup..."
            openssl enc -aes-256-cbc -salt -in "$backup_file" -out "$backup_file.enc" -pass pass:"$ENCRYPT_PASSWORD"
            rm "$backup_file"
            backup_file="$backup_file.enc"
            log "Backup encriptado: $backup_file"
        fi
        
        # Verificar integridad del backup
        log "Verificando integridad del backup..."
        if [ "$COMPRESS" = true ] && [[ "$backup_file" == *.gz ]]; then
            gzip -t "$backup_file"
        fi
        
        log "Backup completado y verificado: $backup_file"
        
        # Mostrar estadísticas del backup
        local backup_size=$(du -h "$backup_file" | cut -f1)
        log "Tamaño del backup: $backup_size"
        
        # Crear archivo de metadatos
        local metadata_file="$backup_file.meta"
        cat > "$metadata_file" << EOF
Backup del Sistema POS Odata
Fecha: $(date)
Archivo: $backup_file
Tamaño: $backup_size
Base de datos: $DB_NAME
Host: $DB_HOST:$DB_PORT
Usuario: $DB_USER
Comprimido: $COMPRESS
Encriptado: $ENCRYPT
EOF
        
        log "Metadatos guardados en: $metadata_file"
        
    else
        log "ERROR: Fallo en el backup de la base de datos"
        exit 1
    fi
}

# Función de backup de archivos de configuración
backup_config_files() {
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local config_backup="$BACKUP_DIR/config_backup_$timestamp.tar.gz"
    
    log "Creando backup de archivos de configuración..."
    
    # Crear backup de archivos importantes
    tar -czf "$config_backup" \
        -C /app \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='logs/*' \
        --exclude='uploads/*' \
        --exclude='instance/*' \
        . > /dev/null 2> >(tee -a /var/log/backup-error.log >&2)
    
    if [ -f "$config_backup" ]; then
        log "Backup de configuración completado: $config_backup"
        local config_size=$(du -h "$config_backup" | cut -f1)
        log "Tamaño del backup de configuración: $config_size"
    else
        log "ERROR: No se pudo crear backup de configuración. Revisa /var/log/backup-error.log"
    fi
}

# Función de backup de logs
backup_logs() {
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local logs_backup="$BACKUP_DIR/logs_backup_$timestamp.tar.gz"
    
    log "Creando backup de logs..."
    
    # Crear backup de logs (solo los últimos 7 días)
    find /app/logs -name "*.log" -mtime -7 -print0 | xargs -0 tar -czf "$logs_backup" > /dev/null 2> >(tee -a /var/log/backup-error.log >&2)
    
    if [ -f "$logs_backup" ]; then
        log "Backup de logs completado: $logs_backup"
        local logs_size=$(du -h "$logs_backup" | cut -f1)
        log "Tamaño del backup de logs: $logs_size"
    else
        log "ADVERTENCIA: No se pudo crear backup de logs o no se encontraron logs recientes. Revisa /var/log/backup-error.log"
    fi
}

# Función principal
main() {
    log "=== INICIANDO PROCESO DE BACKUP AUTOMÁTICO ==="
    
    # Verificar variables de entorno
    if [ -z "$DB_PASSWORD" ]; then
        log "ERROR: Variable DB_PASSWORD no está definida"
        exit 1
    fi
    
    # Crear directorio de backup
    mkdir -p "$BACKUP_DIR"
    
    # Ejecutar backups
    backup_database
    backup_config_files
    backup_logs
    
    # Limpiar backups antiguos
    cleanup_old_backups
    
    # Mostrar resumen
    log "=== RESUMEN DEL BACKUP ==="
    log "Backups disponibles:"
    ls -lh "$BACKUP_DIR"/*.sql* 2>/dev/null || log "No hay backups de base de datos"
    ls -lh "$BACKUP_DIR"/*.tar.gz 2>/dev/null || log "No hay backups de archivos"
    
    # Mostrar espacio en disco
    local disk_usage=$(df -h "$BACKUP_DIR" | tail -1 | awk '{print $5}')
    log "Uso de disco en directorio de backup: $disk_usage"
    
    log "=== PROCESO DE BACKUP COMPLETADO ==="
}

# Ejecutar función principal
main "$@"
