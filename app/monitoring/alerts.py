"""
Sistema de Alertas - Sistema POS O'Data
======================================
Sistema profesional de alertas y notificaciones
"""

import logging
import smtplib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
try:
    from email.mime.text import MIMEText as MimeText
    from email.mime.multipart import MIMEMultipart as MimeMultipart
except ImportError:
    # Fallback para Python 3.13
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
from dataclasses import dataclass, asdict
from enum import Enum
import os
import requests
from app.config.redis_config import get_redis_client, is_redis_available

logger = logging.getLogger(__name__)

class AlertLevel(Enum):
    """Niveles de alerta"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AlertType(Enum):
    """Tipos de alerta"""
    SYSTEM = "system"
    PERFORMANCE = "performance"
    SECURITY = "security"
    BUSINESS = "business"
    DATABASE = "database"
    REDIS = "redis"
    API = "api"

@dataclass
class Alert:
    """Estructura de una alerta"""
    id: str
    type: AlertType
    level: AlertLevel
    title: str
    message: str
    timestamp: datetime
    source: str
    metadata: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[datetime] = None

class AlertManager:
    """Gestor de alertas profesional"""
    
    def __init__(self):
        self.alert_history: List[Alert] = []
        self.alert_rules: Dict[str, Dict] = {}
        self.notification_channels: Dict[str, Dict] = {}
        self.rate_limits: Dict[str, datetime] = {}
        self._setup_default_rules()
        self._setup_notification_channels()
    
    def _setup_default_rules(self):
        """Configurar reglas de alerta por defecto"""
        self.alert_rules = {
            "high_error_rate": {
                "condition": lambda metrics: metrics.get("error_rate", 0) > 5.0,
                "level": AlertLevel.ERROR,
                "type": AlertType.SYSTEM,
                "title": "Tasa de errores alta",
                "message": "La tasa de errores ha excedido el 5%",
                "cooldown": 300  # 5 minutos
            },
            "slow_response_time": {
                "condition": lambda metrics: metrics.get("average_response_time_ms", 0) > 2000,
                "level": AlertLevel.WARNING,
                "type": AlertType.PERFORMANCE,
                "title": "Tiempo de respuesta lento",
                "message": "El tiempo de respuesta promedio excede 2 segundos",
                "cooldown": 600  # 10 minutos
            },
            "high_memory_usage": {
                "condition": lambda metrics: metrics.get("memory_usage_percent", 0) > 85,
                "level": AlertLevel.WARNING,
                "type": AlertType.SYSTEM,
                "title": "Uso de memoria alto",
                "message": "El uso de memoria excede el 85%",
                "cooldown": 300
            },
            "database_connection_failed": {
                "condition": lambda health: not health.get("database", {}).get("status") == "healthy",
                "level": AlertLevel.CRITICAL,
                "type": AlertType.DATABASE,
                "title": "Fallo de conexión a base de datos",
                "message": "No se puede conectar a la base de datos",
                "cooldown": 60
            },
            "redis_connection_failed": {
                "condition": lambda health: not health.get("redis", {}).get("status") == "healthy",
                "level": AlertLevel.WARNING,
                "type": AlertType.REDIS,
                "title": "Fallo de conexión a Redis",
                "message": "No se puede conectar a Redis",
                "cooldown": 300
            },
            "rate_limit_exceeded": {
                "condition": lambda metrics: metrics.get("rate_limit_hits", 0) > 100,
                "level": AlertLevel.WARNING,
                "type": AlertType.SECURITY,
                "title": "Rate limiting activo",
                "message": "Se han bloqueado más de 100 requests por rate limiting",
                "cooldown": 600
            }
        }
    
    def _setup_notification_channels(self):
        """Configurar canales de notificación"""
        self.notification_channels = {
            "email": {
                "enabled": os.environ.get("ALERT_EMAIL_ENABLED", "false").lower() == "true",
                "smtp_server": os.environ.get("ALERT_SMTP_SERVER", "smtp.gmail.com"),
                "smtp_port": int(os.environ.get("ALERT_SMTP_PORT", "587")),
                "username": os.environ.get("ALERT_EMAIL_USERNAME"),
                "password": os.environ.get("ALERT_EMAIL_PASSWORD"),
                "recipients": os.environ.get("ALERT_EMAIL_RECIPIENTS", "").split(",")
            },
            "slack": {
                "enabled": os.environ.get("ALERT_SLACK_ENABLED", "false").lower() == "true",
                "webhook_url": os.environ.get("ALERT_SLACK_WEBHOOK_URL"),
                "channel": os.environ.get("ALERT_SLACK_CHANNEL", "#alerts")
            },
            "webhook": {
                "enabled": os.environ.get("ALERT_WEBHOOK_ENABLED", "false").lower() == "true",
                "url": os.environ.get("ALERT_WEBHOOK_URL"),
                "headers": json.loads(os.environ.get("ALERT_WEBHOOK_HEADERS", "{}"))
            }
        }
    
    def check_alerts(self, metrics: Dict[str, Any], health: Dict[str, Any]):
        """Verificar condiciones de alerta"""
        current_time = datetime.utcnow()
        
        for rule_name, rule in self.alert_rules.items():
            try:
                # Verificar cooldown
                if rule_name in self.rate_limits:
                    if current_time - self.rate_limits[rule_name] < timedelta(seconds=rule["cooldown"]):
                        continue
                
                # Verificar condición
                if rule["condition"](metrics) or rule["condition"](health):
                    alert = Alert(
                        id=f"{rule_name}_{int(current_time.timestamp())}",
                        type=rule["type"],
                        level=rule["level"],
                        title=rule["title"],
                        message=rule["message"],
                        timestamp=current_time,
                        source="monitoring_system",
                        metadata={
                            "rule": rule_name,
                            "metrics": metrics,
                            "health": health
                        }
                    )
                    
                    self._process_alert(alert)
                    self.rate_limits[rule_name] = current_time
                    
            except Exception as e:
                logger.error(f"Error checking alert rule {rule_name}: {e}")
    
    def _process_alert(self, alert: Alert):
        """Procesar una alerta"""
        logger.warning(f"Alert triggered: {alert.title} - {alert.message}")
        
        # Agregar a historial
        self.alert_history.append(alert)
        
        # Mantener solo últimas 1000 alertas
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        # Enviar notificaciones
        self._send_notifications(alert)
        
        # Guardar en Redis si está disponible
        self._save_alert_to_redis(alert)
    
    def _send_notifications(self, alert: Alert):
        """Enviar notificaciones por todos los canales configurados"""
        for channel_name, channel_config in self.notification_channels.items():
            if not channel_config.get("enabled", False):
                continue
            
            try:
                if channel_name == "email":
                    self._send_email_alert(alert, channel_config)
                elif channel_name == "slack":
                    self._send_slack_alert(alert, channel_config)
                elif channel_name == "webhook":
                    self._send_webhook_alert(alert, channel_config)
            except Exception as e:
                logger.error(f"Failed to send {channel_name} notification: {e}")
    
    def _send_email_alert(self, alert: Alert, config: Dict[str, Any]):
        """Enviar alerta por email"""
        if not config.get("recipients"):
            return
        
        msg = MimeMultipart()
        msg['From'] = config["username"]
        msg['To'] = ", ".join(config["recipients"])
        msg['Subject'] = f"[{alert.level.value.upper()}] {alert.title}"
        
        body = f"""
        <h2>🚨 Alerta del Sistema POS O'Data</h2>
        
        <p><strong>Tipo:</strong> {alert.type.value}</p>
        <p><strong>Nivel:</strong> {alert.level.value.upper()}</p>
        <p><strong>Título:</strong> {alert.title}</p>
        <p><strong>Mensaje:</strong> {alert.message}</p>
        <p><strong>Timestamp:</strong> {alert.timestamp.isoformat()}</p>
        <p><strong>Fuente:</strong> {alert.source}</p>
        
        <h3>Metadatos:</h3>
        <pre>{json.dumps(alert.metadata, indent=2)}</pre>
        
        <hr>
        <p><em>Sistema de Monitoreo POS O'Data</em></p>
        """
        
        msg.attach(MimeText(body, 'html'))
        
        with smtplib.SMTP(config["smtp_server"], config["smtp_port"]) as server:
            server.starttls()
            server.login(config["username"], config["password"])
            server.send_message(msg)
        
        logger.info(f"Email alert sent for: {alert.title}")
    
    def _send_slack_alert(self, alert: Alert, config: Dict[str, Any]):
        """Enviar alerta a Slack"""
        if not config.get("webhook_url"):
            return
        
        # Determinar color según nivel
        color_map = {
            AlertLevel.INFO: "#36a64f",
            AlertLevel.WARNING: "#ffaa00",
            AlertLevel.ERROR: "#ff0000",
            AlertLevel.CRITICAL: "#8b0000"
        }
        
        payload = {
            "channel": config["channel"],
            "username": "POS O'Data Monitor",
            "icon_emoji": ":warning:",
            "attachments": [
                {
                    "color": color_map.get(alert.level, "#ff0000"),
                    "title": alert.title,
                    "text": alert.message,
                    "fields": [
                        {
                            "title": "Tipo",
                            "value": alert.type.value,
                            "short": True
                        },
                        {
                            "title": "Nivel",
                            "value": alert.level.value.upper(),
                            "short": True
                        },
                        {
                            "title": "Timestamp",
                            "value": alert.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"),
                            "short": False
                        }
                    ],
                    "footer": "Sistema POS O'Data",
                    "ts": int(alert.timestamp.timestamp())
                }
            ]
        }
        
        response = requests.post(config["webhook_url"], json=payload)
        response.raise_for_status()
        
        logger.info(f"Slack alert sent for: {alert.title}")
    
    def _send_webhook_alert(self, alert: Alert, config: Dict[str, Any]):
        """Enviar alerta a webhook personalizado"""
        if not config.get("url"):
            return
        
        payload = {
            "alert": asdict(alert),
            "timestamp": alert.timestamp.isoformat()
        }
        
        headers = {
            "Content-Type": "application/json",
            **config.get("headers", {})
        }
        
        response = requests.post(config["url"], json=payload, headers=headers)
        response.raise_for_status()
        
        logger.info(f"Webhook alert sent for: {alert.title}")
    
    def _save_alert_to_redis(self, alert: Alert):
        """Guardar alerta en Redis"""
        if not is_redis_available():
            return
        
        try:
            redis_client = get_redis_client()
            if redis_client:
                alert_data = {
                    "id": alert.id,
                    "type": alert.type.value,
                    "level": alert.level.value,
                    "title": alert.title,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "source": alert.source,
                    "metadata": json.dumps(alert.metadata),
                    "resolved": alert.resolved
                }
                
                # Guardar alerta individual
                redis_client.hset(f"alert:{alert.id}", mapping=alert_data)
                redis_client.expire(f"alert:{alert.id}", 86400 * 7)  # 7 días
                
                # Agregar a lista de alertas recientes
                redis_client.lpush("recent_alerts", alert.id)
                redis_client.ltrim("recent_alerts", 0, 99)  # Mantener solo 100
                redis_client.expire("recent_alerts", 86400)  # 1 día
                
        except Exception as e:
            logger.error(f"Failed to save alert to Redis: {e}")
    
    def get_recent_alerts(self, limit: int = 50) -> List[Alert]:
        """Obtener alertas recientes"""
        return sorted(
            self.alert_history,
            key=lambda x: x.timestamp,
            reverse=True
        )[:limit]
    
    def resolve_alert(self, alert_id: str):
        """Resolver una alerta"""
        for alert in self.alert_history:
            if alert.id == alert_id:
                alert.resolved = True
                alert.resolved_at = datetime.utcnow()
                logger.info(f"Alert resolved: {alert_id}")
                break
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de alertas"""
        now = datetime.utcnow()
        last_hour = now - timedelta(hours=1)
        last_day = now - timedelta(days=1)
        
        recent_alerts = [a for a in self.alert_history if a.timestamp > last_hour]
        daily_alerts = [a for a in self.alert_history if a.timestamp > last_day]
        
        stats = {
            "total_alerts": len(self.alert_history),
            "alerts_last_hour": len(recent_alerts),
            "alerts_last_day": len(daily_alerts),
            "unresolved_alerts": len([a for a in self.alert_history if not a.resolved]),
            "alerts_by_level": {},
            "alerts_by_type": {}
        }
        
        # Contar por nivel
        for level in AlertLevel:
            stats["alerts_by_level"][level.value] = len([
                a for a in self.alert_history if a.level == level
            ])
        
        # Contar por tipo
        for alert_type in AlertType:
            stats["alerts_by_type"][alert_type.value] = len([
                a for a in self.alert_history if a.type == alert_type
            ])
        
        return stats

# Instancia global del gestor de alertas
alert_manager = AlertManager()

def check_and_send_alerts(metrics: Dict[str, Any], health: Dict[str, Any]):
    """Función helper para verificar y enviar alertas"""
    alert_manager.check_alerts(metrics, health)

def get_alert_stats() -> Dict[str, Any]:
    """Función helper para obtener estadísticas de alertas"""
    return alert_manager.get_alert_stats()

def get_recent_alerts(limit: int = 50) -> List[Alert]:
    """Función helper para obtener alertas recientes"""
    return alert_manager.get_recent_alerts(limit)
