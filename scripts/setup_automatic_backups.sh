#!/bin/bash
# Script para Configurar Backups Automáticos
# Sistema POS O'Data v2.0.2-enterprise

# Configuración
BACKUP_DIR="/app/backups"
RETENTION_DAYS=30
BACKUP_SCHEDULE="0 2 * * *"  # Diario a las 2:00 AM

echo "========================================"
echo "CONFIGURACIÓN DE BACKUPS AUTOMÁTICOS"
echo "Sistema POS O'Data v2.0.2-enterprise"
echo "========================================"
echo ""

# Crear directorio de backups
mkdir -p "$BACKUP_DIR"

# Crear script de backup
cat > /app/scripts/run_backup.sh << 'EOF'
#!/bin/bash
cd /app
python scripts/backup_database.py --backup-dir /app/backups --retention-days 30
EOF

chmod +x /app/scripts/run_backup.sh

# Agregar a crontab si no existe
(crontab -l 2>/dev/null | grep -v "backup_database.py"; echo "$BACKUP_SCHEDULE cd /app && python scripts/backup_database.py --backup-dir $BACKUP_DIR --retention-days $RETENTION_DAYS >> /app/logs/backup.log 2>&1") | crontab -

echo "✅ Backups automáticos configurados"
echo "   Horario: $BACKUP_SCHEDULE"
echo "   Directorio: $BACKUP_DIR"
echo "   Retención: $RETENTION_DAYS días"
echo ""
echo "Para verificar: crontab -l"
echo "Para probar manualmente: python scripts/backup_database.py"

