# Script de Backup desde el Host (PowerShell)
# Sistema POS O'Data v2.0.2-enterprise
# Este script debe ejecutarse desde el host Windows

$BACKUP_DIR = ".\backups"
$RETENTION_DAYS = 30
$TIMESTAMP = Get-Date -Format "yyyyMMdd_HHmmss"
$BACKUP_FILE = "$BACKUP_DIR\pos_odata_backup_$TIMESTAMP.dump"

# Crear directorio si no existe
if (-not (Test-Path $BACKUP_DIR)) {
    New-Item -ItemType Directory -Path $BACKUP_DIR -Force | Out-Null
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "BACKUP DE BASE DE DATOS" -ForegroundColor Yellow
Write-Host "Sistema POS O'Data v2.0.2-enterprise" -ForegroundColor Yellow
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Crear backup usando docker exec
Write-Host "📦 Creando backup: $(Split-Path $BACKUP_FILE -Leaf)" -ForegroundColor Green
docker-compose -f docker-compose.production.yml exec -T postgres pg_dump -U pos_user -d pos_odata -F c -f /backups/backup_${TIMESTAMP}.dump

if ($LASTEXITCODE -eq 0) {
    # Copiar backup al host
    Write-Host "📥 Copiando backup al host..." -ForegroundColor Green
    docker-compose -f docker-compose.production.yml cp postgres:/backups/backup_${TIMESTAMP}.dump $BACKUP_FILE
    
    if (Test-Path $BACKUP_FILE) {
        # Comprimir backup usando PowerShell
        Write-Host "🗜️  Comprimiendo backup..." -ForegroundColor Green
        $BACKUP_FILE_GZ = "$BACKUP_FILE.gz"
        
        $inputFile = [System.IO.File]::OpenRead($BACKUP_FILE)
        $outputFile = [System.IO.File]::Create($BACKUP_FILE_GZ)
        $gzipStream = New-Object System.IO.Compression.GZipStream $outputFile, ([IO.Compression.CompressionMode]::Compress)
        $inputFile.CopyTo($gzipStream)
        $gzipStream.Close()
        $outputFile.Close()
        $inputFile.Close()
        
        # Eliminar archivo sin comprimir
        Remove-Item $BACKUP_FILE
        
        # Obtener tamaño
        $FILE_SIZE = (Get-Item $BACKUP_FILE_GZ).Length / 1MB
        
        Write-Host "✅ Backup creado exitosamente: $(Split-Path $BACKUP_FILE_GZ -Leaf)" -ForegroundColor Green
        Write-Host "   Tamaño: $([math]::Round($FILE_SIZE, 2)) MB" -ForegroundColor White
        Write-Host "   Ubicación: $BACKUP_FILE_GZ" -ForegroundColor White
        Write-Host ""
        
        # Limpiar backups antiguos
        Write-Host "🗑️  Limpiando backups antiguos (más de $RETENTION_DAYS días)..." -ForegroundColor Yellow
        $cutoffDate = (Get-Date).AddDays(-$RETENTION_DAYS)
        Get-ChildItem -Path $BACKUP_DIR -Filter "pos_odata_backup_*.dump.gz" | 
            Where-Object { $_.LastWriteTime -lt $cutoffDate } | 
            Remove-Item -Force
        
        Write-Host "✅ Limpieza completada" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "BACKUP COMPLETADO" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
    } else {
        Write-Host "❌ Error: No se pudo copiar el backup al host" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Error: No se pudo crear el backup" -ForegroundColor Red
    exit 1
}

