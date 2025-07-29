#!/bin/bash
set -e

echo "Iniciando aplicación POS Odata..."

# Función para logging
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Verificar variables de entorno críticas
if [ -z "$FLASK_APP" ]; then
    log "ERROR: FLASK_APP no está definido"
    exit 1
fi

# Esperar a que la base de datos esté disponible (si se usa)
if [ -n "$DATABASE_URL" ]; then
    log "Esperando a que la base de datos esté disponible..."
    python scripts/wait-for-db.py
    log "Base de datos disponible!"
fi

# Ejecutar migraciones si es necesario
if [ "$FLASK_ENV" = "production" ] && [ -n "$DATABASE_URL" ]; then
    log "Ejecutando migraciones de base de datos..."
    flask db upgrade || log "ADVERTENCIA: No se pudieron ejecutar las migraciones"
fi

# Crear directorios necesarios
mkdir -p logs
touch logs/app.log

log "Configuración completada. Iniciando aplicación..."

# Ejecutar el comando pasado como argumentos
exec "$@"
