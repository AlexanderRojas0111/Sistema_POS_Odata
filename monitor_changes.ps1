# ==============================================
# MONITOR DE CAMBIOS AUTOMATICO
# Sistema POS Sabrositas v2.0.0 Enterprise
# ==============================================

param(
    [int]$IntervalSeconds = 30,
    [switch]$RunOnce = $false
)

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogMessage = "[$Timestamp] [$Level] $Message"
    
    Write-Host $LogMessage
    
    if (!(Test-Path "logs")) {
        New-Item -ItemType Directory -Path "logs" -Force | Out-Null
    }
    
    $LogMessage | Out-File -FilePath "logs/change_monitor.log" -Append -Encoding UTF8
}

function Test-ForChanges {
    try {
        $watchPatterns = @(
            "app/**/*.py",
            "frontend/src/**/*.tsx",
            "frontend/src/**/*.ts",
            "requirements.txt",
            "frontend/package.json",
            "*.py"
        )
        
        $lastCheckFile = "logs/last_change_check.txt"
        $lastCheck = Get-Date (Get-Content $lastCheckFile -ErrorAction SilentlyContinue) -ErrorAction SilentlyContinue
        if (!$lastCheck) {
            $lastCheck = (Get-Date).AddDays(-1)
        }
        
        $hasChanges = $false
        $changedFiles = @()
        
        foreach ($pattern in $watchPatterns) {
            $files = Get-ChildItem -Path $pattern -Recurse -ErrorAction SilentlyContinue
            foreach ($file in $files) {
                if ($file.LastWriteTime -gt $lastCheck) {
                    $hasChanges = $true
                    $changedFiles += $file.FullName
                }
            }
        }
        
        # Verificar cambios en Git
        try {
            $gitStatus = git status --porcelain 2>$null
            if ($LASTEXITCODE -eq 0 -and $gitStatus) {
                $hasChanges = $true
                $changedFiles += "Git changes detected"
            }
        } catch {
            # Git no disponible
        }
        
        if ($hasChanges) {
            Write-Log "Cambios detectados en: $($changedFiles -join ', ')" "CHANGE"
        }
        
        return $hasChanges
        
    } catch {
        Write-Log "Error verificando cambios: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Update-LastCheck {
    try {
        $lastCheckFile = "logs/last_change_check.txt"
        (Get-Date).ToString() | Out-File -FilePath $lastCheckFile -Encoding UTF8
    } catch {
        Write-Log "Error actualizando timestamp: $($_.Exception.Message)" "ERROR"
    }
}

function Invoke-AutoDeploy {
    try {
        Write-Log "Ejecutando despliegue automatico..." "DEPLOY"
        
        $result = & ".\final_auto_deploy.ps1" -ForceRestart:$false -BackendOnly:$false
        
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Despliegue automatico completado exitosamente" "SUCCESS"
        } else {
            Write-Log "Despliegue automatico fallo con codigo $LASTEXITCODE" "ERROR"
        }
        
    } catch {
        Write-Log "Error ejecutando despliegue automatico: $($_.Exception.Message)" "ERROR"
    }
}

function Start-ChangeMonitor {
    Write-Host ""
    Write-Host "MONITOR DE CAMBIOS AUTOMATICO" -ForegroundColor Cyan
    Write-Host "=============================" -ForegroundColor Cyan
    Write-Host "Sistema POS Sabrositas v2.0.0 Enterprise" -ForegroundColor Yellow
    Write-Host "Intervalo: $IntervalSeconds segundos" -ForegroundColor Green
    Write-Host "Directorio: $(Get-Location)" -ForegroundColor Green
    Write-Host ""
    
    Write-Log "Monitor de cambios iniciado (Intervalo: $IntervalSeconds segundos)" "START"
    
    $iteration = 0
    
    do {
        $iteration++
        
        Write-Host "Verificacion #$iteration - $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Cyan
        
        if (Test-ForChanges) {
            Write-Host "ACTUALIZACIONES DETECTADAS - Iniciando despliegue automatico..." -ForegroundColor Yellow
            Invoke-AutoDeploy
            
            if ($RunOnce) {
                Write-Log "Monitor completado (modo RunOnce)" "COMPLETE"
                break
            }
        } else {
            Write-Host "Sin cambios detectados" -ForegroundColor Green
        }
        
        Update-LastCheck
        
        if (-not $RunOnce) {
            Start-Sleep -Seconds $IntervalSeconds
        }
        
    } while (-not $RunOnce)
    
    Write-Log "Monitor de cambios detenido" "STOP"
    Write-Host ""
    Write-Host "Monitor completado. Log guardado en: logs/change_monitor.log" -ForegroundColor Green
}

try {
    Start-ChangeMonitor
} catch {
    Write-Log "Error fatal en monitor: $($_.Exception.Message)" "FATAL"
    exit 1
}
