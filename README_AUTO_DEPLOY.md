# Sistema de Despliegue Automático - Sistema POS Sabrositas v2.0.0

## 🚀 Descripción

Sistema de despliegue automático que detecta cambios en el código y actualiza el sistema automáticamente, asegurando que siempre esté ejecutándose la versión más reciente.

## 📋 Archivos del Sistema

### Scripts Principales
- `final_auto_deploy.ps1` - Sistema principal de despliegue automático
- `monitor_changes.ps1` - Monitor de cambios en tiempo real
- `auto_deploy_simple.ps1` - Versión simplificada del despliegue
- `deploy_on_update.ps1` - Despliegue rápido para cambios específicos

### Scripts de Configuración
- `setup_auto_deploy.ps1` - Configuración inicial del sistema
- `start_sabrositas_auto.ps1` - Script de inicio automático

### Archivos de Configuración
- `auto_deploy_config.env` - Configuración del sistema
- `logs/auto_deploy.log` - Log del sistema de despliegue
- `logs/change_monitor.log` - Log del monitor de cambios

## 🎯 Funcionalidades

### ✅ Despliegue Automático
- **Detección de Cambios**: Monitorea archivos Python, TypeScript, y configuraciones
- **Backup Automático**: Crea backups de la base de datos antes de cada despliegue
- **Actualización de Dependencias**: Actualiza automáticamente pip y npm
- **Reinicio de Servicios**: Detiene y reinicia backend y frontend
- **Verificación de Estado**: Confirma que los servicios estén funcionando

### 📁 Archivos Monitoreados
- `app/**/*.py` - Código Python del backend
- `frontend/src/**/*.tsx` - Componentes React
- `frontend/src/**/*.ts` - Código TypeScript
- `requirements.txt` - Dependencias Python
- `frontend/package.json` - Dependencias Node.js
- `*.py` - Scripts Python del proyecto
- Cambios en Git

## 🚀 Comandos Disponibles

### Despliegue Manual
```powershell
# Despliegue completo (backend + frontend)
.\final_auto_deploy.ps1

# Despliegue forzado (ignora detección de cambios)
.\final_auto_deploy.ps1 -ForceRestart

# Solo backend (más rápido y confiable)
.\final_auto_deploy.ps1 -BackendOnly
```

### Monitor de Cambios
```powershell
# Monitor continuo (verificación cada 30 segundos)
.\monitor_changes.ps1

# Monitor con intervalo personalizado
.\monitor_changes.ps1 -IntervalSeconds 60

# Verificación única
.\monitor_changes.ps1 -RunOnce
```

### Despliegue Rápido
```powershell
# Despliegue rápido para cambios menores
.\deploy_on_update.ps1
```

## 📊 Proceso de Despliegue

### Fase 1: Backup
- Crea backup de la base de datos actual
- Timestamp: `pos_odata_backup_YYYYMMDD_HHMMSS.db`

### Fase 2: Detener Servicios
- Detiene procesos Python (backend)
- Detiene procesos Node.js (frontend)

### Fase 3: Actualizar Dependencias
- `pip install -r requirements.txt`
- `npm install` (en frontend)

### Fase 4: Iniciar Backend
- Ejecuta `python main.py`
- Verifica health check en `http://localhost:8000/api/v1/health`
- Timeout: 60 segundos

### Fase 5: Iniciar Frontend (Opcional)
- Ejecuta `npm run dev` (en frontend)
- Verifica en `http://localhost:5173`
- Timeout: 30 segundos

### Fase 6: Verificación Final
- Confirma que ambos servicios estén funcionando
- Genera reporte de estado

## 🔧 Configuración

### Variables de Entorno
```env
MONITOR_INTERVAL_SECONDS=30
AUTO_DEPLOY_ON_STARTUP=true
SKIP_BACKUP_ON_AUTO_DEPLOY=false
BACKEND_PORT=8000
FRONTEND_PORT=5173
HEALTH_CHECK_TIMEOUT=10
```

### Logs
- **Ubicación**: `logs/auto_deploy.log`
- **Rotación**: Automática (30 días)
- **Tamaño máximo**: 100MB

### Backups
- **Ubicación**: `backups/`
- **Retención**: 7 días
- **Formato**: `pos_odata_backup_YYYYMMDD_HHMMSS.db`

## 📈 Monitoreo

### Estados del Sistema
- ✅ **Backend Funcionando**: HTTP 200 en `/api/v1/health`
- ✅ **Frontend Funcionando**: HTTP 200 en `http://localhost:5173`
- ❌ **Error**: Servicio no responde o devuelve error

### Logs Importantes
```
[SUCCESS] Backend disponible y funcionando
[SUCCESS] Frontend funcionando correctamente
[ERROR] Backend no disponible después de 30 intentos
[CHANGE] Cambios detectados en: app/api/v1/sales.py
[DEPLOY] Ejecutando despliegue automático...
```

## 🛠️ Solución de Problemas

### Backend No Inicia
1. Verificar que el puerto 8000 esté libre
2. Revisar logs en `logs/auto_deploy.log`
3. Ejecutar manualmente: `python main.py`

### Frontend No Inicia
1. Verificar que el puerto 5173 esté libre
2. Ejecutar en frontend: `npm install && npm run dev`
3. Usar modo backend-only: `-BackendOnly`

### Dependencias No Actualizan
1. Verificar conexión a internet
2. Limpiar cache: `pip cache purge` y `npm cache clean`
3. Reinstalar manualmente

## 🎯 Casos de Uso

### Desarrollo Diario
```powershell
# Ejecutar monitor en background
Start-Process powershell -ArgumentList "-File", ".\monitor_changes.ps1" -WindowStyle Hidden
```

### Actualización Manual
```powershell
# Despliegue completo después de cambios importantes
.\final_auto_deploy.ps1 -ForceRestart
```

### Solo Backend
```powershell
# Para cambios solo en backend (más rápido)
.\final_auto_deploy.ps1 -BackendOnly -ForceRestart
```

## 📋 Checklist de Despliegue

- [ ] Backup de base de datos creado
- [ ] Servicios anteriores detenidos
- [ ] Dependencias actualizadas
- [ ] Backend iniciado y funcionando
- [ ] Frontend iniciado (si aplica)
- [ ] Health checks exitosos
- [ ] Logs verificados

## 🔒 Seguridad

- Los backups contienen datos sensibles
- Los logs pueden contener información del sistema
- El sistema requiere permisos de administrador para tareas programadas
- Los tokens JWT se manejan de forma segura

## 📞 Soporte

Para problemas o consultas:
1. Revisar logs en `logs/auto_deploy.log`
2. Verificar estado de servicios manualmente
3. Ejecutar despliegue manual con `-ForceRestart`
4. Contactar al equipo de desarrollo

---

**Sistema POS Sabrositas v2.0.0 Enterprise**  
*Las Arepas Cuadradas - Despliegue Automático Profesional*
