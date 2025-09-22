# ==============================================
# SISTEMA DE DESPLIEGUE AUTOMATICO FINAL
# Sistema POS Sabrositas v2.0.0 Enterprise
# ==============================================

param(
    [switch]$ForceRestart = $false,
    [switch]$BackendOnly = $false
)

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    Write-Host $LogMessage
    
    if (!(Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    }
    $LogMessage | Out-File -FilePath "logs/auto_deploy.log" -Append -Encoding UTF8
}

function Test-HasChanges {
    try {
        $gitStatus = git status --porcelain 2>$null
        if ($LASTEXITCODE -eq 0 -and $gitStatus) {
            return $true
        }
        
        $keyFiles = @("requirements.txt", "app", "*.py")
        $lastCheck = Get-Date (Get-Content "logs/auto_deploy.log" -Tail 10 -ErrorAction SilentlyContinue | Select-String "COMPLETED" | Select-Object -First 1) -ErrorAction SilentlyContinue
        if (!$lastCheck) { return $true }
        
        foreach ($pattern in $keyFiles) {
            $files = Get-ChildItem -Path $pattern -Recurse -ErrorAction SilentlyContinue
            foreach ($file in $files) {
                if ($file.LastWriteTime -gt $lastCheck) {
                    return $true
                }
            }
        }
        
        return $false
    } catch {
        return $true
    }
}

function New-Backup {
    $backupFile = "backups\pos_odata_backup_$(Get-Date -Format 'yyyyMMdd_HHmmss').db"
    if (!(Test-Path "backups")) {
        New-Item -ItemType Directory -Path "backups" -Force | Out-Null
    }
    
    if (Test-Path "instance\pos_odata.db") {
        Copy-Item "instance\pos_odata.db" $backupFile
        Write-Log "Backup creado: $backupFile" "SUCCESS"
    }
}

function Stop-Backend {
    Write-Log "Deteniendo backend..." "INFO"
    Get-Process -Name "python" -ErrorAction SilentlyContinue | 
        Where-Object { $_.CommandLine -like "*main.py*" } | 
        Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Log "Backend detenido" "SUCCESS"
}

function Update-Backend {
    Write-Log "Actualizando dependencias del backend..." "INFO"
    try {
        pip install -r requirements.txt --quiet
        Write-Log "Dependencias del backend actualizadas" "SUCCESS"
    } catch {
        Write-Log "Error actualizando dependencias: $($_.Exception.Message)" "ERROR"
        throw
    }
}

function Start-Backend {
    Write-Log "Iniciando backend..." "INFO"
    
    try {
        Start-Process -FilePath "python" -ArgumentList "main.py" -WindowStyle Hidden
        Write-Log "Backend iniciado" "SUCCESS"
        
        # Esperar que el backend esté disponible
        $maxAttempts = 30
        $attempt = 0
        do {
            Start-Sleep -Seconds 2
            $attempt++
            try {
                $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
                if ($response.StatusCode -eq 200) {
                    Write-Log "Backend disponible y funcionando" "SUCCESS"
                    return $true
                }
            } catch {
                if ($attempt -eq $maxAttempts) {
                    Write-Log "Backend no disponible despues de $maxAttempts intentos" "ERROR"
                    return $false
                }
            }
        } while ($attempt -lt $maxAttempts)
        
        return $false
        
    } catch {
        Write-Log "Error iniciando backend: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Start-Frontend {
    if ($BackendOnly) {
        Write-Log "Frontend omitido (modo BackendOnly)" "INFO"
        return $true
    }
    
    Write-Log "Iniciando frontend..." "INFO"
    
    try {
        # Detener frontend existente
        Get-Process -Name "node" -ErrorAction SilentlyContinue | 
            Where-Object { $_.CommandLine -like "*npm*" -or $_.CommandLine -like "*vite*" } | 
            Stop-Process -Force -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
        
        # Actualizar dependencias del frontend
        Set-Location frontend
        npm install --silent
        Set-Location ..
        
        # Iniciar frontend
        Set-Location frontend
        Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WindowStyle Hidden
        Set-Location ..
        
        Write-Log "Frontend iniciado (verificacion manual requerida)" "SUCCESS"
        return $true
        
    } catch {
        Write-Log "Error iniciando frontend: $($_.Exception.Message)" "ERROR"
        Set-Location ..
        return $false
    }
}

function Test-Backend {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/api/v1/health" -UseBasicParsing -TimeoutSec 10 -ErrorAction Stop
        if ($response.StatusCode -eq 200) {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

function Start-AutoDeploy {
    Write-Host ""
    Write-Host "SISTEMA DE DESPLIEGUE AUTOMATICO - Sistema POS Sabrositas v2.0.0" -ForegroundColor Cyan
    Write-Host "=================================================================" -ForegroundColor Cyan
    Write-Host "Las Arepas Cuadradas - Enterprise Auto-Deployment" -ForegroundColor Yellow
    Write-Host "Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Green
    Write-Host ""
    
    Write-Log "Iniciando despliegue automatico" "INFO"
    
    if (-not $ForceRestart -and -not (Test-HasChanges)) {
        Write-Log "No se detectaron cambios. Use -ForceRestart para forzar el despliegue" "INFO"
        return
    }
    
    try {
        # FASE 1: BACKUP
        Write-Log "FASE 1: BACKUP" "INFO"
        New-Backup
        
        # FASE 2: DETENER BACKEND
        Write-Log "FASE 2: DETENER BACKEND" "INFO"
        Stop-Backend
        
        # FASE 3: ACTUALIZAR BACKEND
        Write-Log "FASE 3: ACTUALIZAR BACKEND" "INFO"
        Update-Backend
        
        # FASE 4: INICIAR BACKEND
        Write-Log "FASE 4: INICIAR BACKEND" "INFO"
        $backendOk = Start-Backend
        
        if (-not $backendOk) {
            Write-Log "Backend no pudo iniciarse correctamente" "ERROR"
            exit 1
        }
        
        # FASE 5: INICIAR FRONTEND (OPCIONAL)
        if (-not $BackendOnly) {
            Write-Log "FASE 5: INICIAR FRONTEND" "INFO"
            Start-Frontend
        }
        
        # FASE 6: VERIFICACION FINAL
        Write-Log "FASE 6: VERIFICACION FINAL" "INFO"
        $backendWorking = Test-Backend
        
        Write-Host ""
        if ($backendWorking) {
            Write-Host "DESPLIEGUE AUTOMATICO EXITOSO" -ForegroundColor Green
            Write-Host "==============================" -ForegroundColor Green
            Write-Host ""
            Write-Host "URLs del Sistema:" -ForegroundColor Cyan
            Write-Host "   Backend:       http://localhost:8000" -ForegroundColor Green
            Write-Host "   Health Check:  http://localhost:8000/api/v1/health" -ForegroundColor Green
            if (-not $BackendOnly) {
                Write-Host "   Frontend:      http://localhost:5173 (verificar manualmente)" -ForegroundColor Yellow
            }
            Write-Host ""
            Write-Log "Despliegue automatico completado exitosamente" "SUCCESS"
        } else {
            Write-Host "DESPLIEGUE AUTOMATICO CON ERRORES" -ForegroundColor Red
            Write-Host "====================================" -ForegroundColor Red
            Write-Log "Despliegue automatico completado con errores" "ERROR"
            exit 1
        }
        
    } catch {
        Write-Log "Error en despliegue automatico: $($_.Exception.Message)" "ERROR"
        exit 1
    }
}

Start-AutoDeploy
