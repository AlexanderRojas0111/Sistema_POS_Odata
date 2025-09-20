"""
Servicio de Auditoría Avanzado - Sistema POS Sabrositas
Logging detallado, tracking de cambios y análisis de seguridad
"""

import logging
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from sqlalchemy import func, desc, and_, or_
from flask import request, g
from flask_jwt_extended import get_jwt_identity
import ipaddress
from user_agents import parse

from app import db
from app.models.user import User
from app.models.sale import Sale
from app.models.product import Product

logger = logging.getLogger(__name__)

class AuditLevel:
    """Niveles de auditoría"""
    INFO = 'info'
    WARNING = 'warning'
    ERROR = 'error'
    CRITICAL = 'critical'
    SECURITY = 'security'

class AuditCategory:
    """Categorías de eventos de auditoría"""
    AUTH = 'authentication'
    SALES = 'sales'
    INVENTORY = 'inventory'
    USER_MGMT = 'user_management'
    SYSTEM = 'system'
    DATA_ACCESS = 'data_access'
    SECURITY = 'security'
    API = 'api'

class AuditEvent:
    """Modelo de evento de auditoría"""
    
    def __init__(self, 
                 event_type: str,
                 category: str,
                 level: str = AuditLevel.INFO,
                 user_id: Optional[int] = None,
                 description: str = "",
                 details: Optional[Dict] = None,
                 entity_type: Optional[str] = None,
                 entity_id: Optional[Union[int, str]] = None,
                 ip_address: Optional[str] = None,
                 user_agent: Optional[str] = None):
        
        self.event_type = event_type
        self.category = category
        self.level = level
        self.user_id = user_id
        self.description = description
        self.details = details or {}
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.ip_address = ip_address or self._get_client_ip()
        self.user_agent = user_agent or self._get_user_agent()
        self.timestamp = datetime.now()
        
    def _get_client_ip(self) -> str:
        """Obtener IP del cliente"""
        if request:
            return request.environ.get('HTTP_X_FORWARDED_FOR', 
                                     request.environ.get('REMOTE_ADDR', 'unknown'))
        return 'system'
    
    def _get_user_agent(self) -> str:
        """Obtener User Agent"""
        if request:
            return request.headers.get('User-Agent', 'unknown')
        return 'system'

class AuditService:
    """Servicio principal de auditoría"""
    
    def __init__(self):
        self.logger = logging.getLogger('audit')
        self._setup_audit_logger()
    
    def _setup_audit_logger(self):
        """Configurar logger específico para auditoría"""
        if not self.logger.handlers:
            handler = logging.FileHandler('logs/audit.log')
            formatter = logging.Formatter(
                '%(asctime)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
    
    def log_event(self, event: AuditEvent) -> bool:
        """
        Registrar evento de auditoría
        """
        try:
            # Preparar datos del evento
            event_data = {
                'timestamp': event.timestamp.isoformat(),
                'event_type': event.event_type,
                'category': event.category,
                'level': event.level,
                'user_id': event.user_id,
                'description': event.description,
                'details': event.details,
                'entity_type': event.entity_type,
                'entity_id': event.entity_id,
                'ip_address': event.ip_address,
                'user_agent': event.user_agent,
                'session_id': self._get_session_id(),
                'request_id': self._get_request_id()
            }
            
            # Enriquecer con información adicional
            event_data = self._enrich_event_data(event_data)
            
            # Log estructurado
            log_message = f"AUDIT: {json.dumps(event_data, ensure_ascii=False)}"
            
            # Determinar nivel de log
            if event.level == AuditLevel.CRITICAL:
                self.logger.critical(log_message)
            elif event.level == AuditLevel.ERROR:
                self.logger.error(log_message)
            elif event.level == AuditLevel.WARNING:
                self.logger.warning(log_message)
            elif event.level == AuditLevel.SECURITY:
                self.logger.critical(f"SECURITY: {log_message}")
            else:
                self.logger.info(log_message)
            
            # Almacenar en base de datos si es crítico
            if event.level in [AuditLevel.CRITICAL, AuditLevel.SECURITY, AuditLevel.ERROR]:
                self._store_critical_event(event_data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error logging audit event: {str(e)}")
            return False
    
    def _enrich_event_data(self, event_data: Dict) -> Dict:
        """Enriquecer datos del evento con información adicional"""
        try:
            # Información del usuario si está disponible
            if event_data.get('user_id'):
                user = User.query.get(event_data['user_id'])
                if user:
                    event_data['user_info'] = {
                        'username': user.username,
                        'email': user.email,
                        'role': user.role,
                        'is_active': user.is_active
                    }
            
            # Análisis de User Agent
            if event_data.get('user_agent'):
                ua = parse(event_data['user_agent'])
                event_data['device_info'] = {
                    'browser': f"{ua.browser.family} {ua.browser.version_string}",
                    'os': f"{ua.os.family} {ua.os.version_string}",
                    'device': ua.device.family,
                    'is_mobile': ua.is_mobile,
                    'is_bot': ua.is_bot
                }
            
            # Análisis de IP
            if event_data.get('ip_address'):
                event_data['ip_info'] = self._analyze_ip(event_data['ip_address'])
            
            # Hash del evento para integridad
            event_data['integrity_hash'] = self._calculate_event_hash(event_data)
            
            return event_data
            
        except Exception as e:
            logger.warning(f"Error enriching event data: {str(e)}")
            return event_data
    
    def _analyze_ip(self, ip_address: str) -> Dict:
        """Analizar dirección IP"""
        try:
            ip = ipaddress.ip_address(ip_address)
            return {
                'is_private': ip.is_private,
                'is_loopback': ip.is_loopback,
                'is_multicast': ip.is_multicast,
                'version': ip.version,
                'is_suspicious': self._is_suspicious_ip(ip_address)
            }
        except:
            return {'is_suspicious': False}
    
    def _is_suspicious_ip(self, ip_address: str) -> bool:
        """Detectar IPs sospechosas (lista negra simplificada)"""
        suspicious_patterns = [
            '127.0.0.1',  # Localhost (puede ser sospechoso en producción)
            # Agregar más patrones según necesidades
        ]
        return any(pattern in ip_address for pattern in suspicious_patterns)
    
    def _calculate_event_hash(self, event_data: Dict) -> str:
        """Calcular hash para integridad del evento"""
        # Crear string determinístico del evento (sin el hash)
        event_copy = {k: v for k, v in event_data.items() if k != 'integrity_hash'}
        event_string = json.dumps(event_copy, sort_keys=True, ensure_ascii=False)
        return hashlib.sha256(event_string.encode()).hexdigest()
    
    def _store_critical_event(self, event_data: Dict):
        """Almacenar eventos críticos en base de datos"""
        try:
            # Aquí se podría implementar almacenamiento en tabla de auditoría
            # Por ahora solo logueamos
            logger.info(f"Critical event stored: {event_data['event_type']}")
        except Exception as e:
            logger.error(f"Error storing critical event: {str(e)}")
    
    def _get_session_id(self) -> Optional[str]:
        """Obtener ID de sesión"""
        if hasattr(g, 'session_id'):
            return g.session_id
        return None
    
    def _get_request_id(self) -> Optional[str]:
        """Obtener ID de request"""
        if hasattr(g, 'request_id'):
            return g.request_id
        return None
    
    # Métodos de conveniencia para diferentes tipos de eventos
    
    def log_authentication(self, event_type: str, user_id: Optional[int] = None, 
                          success: bool = True, details: Optional[Dict] = None):
        """Log de eventos de autenticación"""
        level = AuditLevel.INFO if success else AuditLevel.WARNING
        
        event = AuditEvent(
            event_type=event_type,
            category=AuditCategory.AUTH,
            level=level,
            user_id=user_id,
            description=f"Authentication event: {event_type}",
            details=details or {}
        )
        
        self.log_event(event)
    
    def log_sale_transaction(self, event_type: str, sale_id: int, user_id: int, 
                           details: Optional[Dict] = None):
        """Log de transacciones de venta"""
        event = AuditEvent(
            event_type=event_type,
            category=AuditCategory.SALES,
            level=AuditLevel.INFO,
            user_id=user_id,
            description=f"Sale transaction: {event_type}",
            details=details or {},
            entity_type='sale',
            entity_id=sale_id
        )
        
        self.log_event(event)
    
    def log_inventory_change(self, event_type: str, product_id: int, user_id: int,
                           old_value: Any, new_value: Any, field: str):
        """Log de cambios en inventario"""
        event = AuditEvent(
            event_type=event_type,
            category=AuditCategory.INVENTORY,
            level=AuditLevel.INFO,
            user_id=user_id,
            description=f"Inventory change: {field}",
            details={
                'field': field,
                'old_value': old_value,
                'new_value': new_value,
                'change_type': 'update'
            },
            entity_type='product',
            entity_id=product_id
        )
        
        self.log_event(event)
    
    def log_security_event(self, event_type: str, description: str, 
                          level: str = AuditLevel.SECURITY, details: Optional[Dict] = None):
        """Log de eventos de seguridad"""
        event = AuditEvent(
            event_type=event_type,
            category=AuditCategory.SECURITY,
            level=level,
            description=description,
            details=details or {}
        )
        
        self.log_event(event)
    
    def log_api_access(self, endpoint: str, method: str, status_code: int,
                      user_id: Optional[int] = None, response_time: Optional[float] = None):
        """Log de acceso a APIs"""
        level = AuditLevel.WARNING if status_code >= 400 else AuditLevel.INFO
        
        event = AuditEvent(
            event_type='api_access',
            category=AuditCategory.API,
            level=level,
            user_id=user_id,
            description=f"API access: {method} {endpoint}",
            details={
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code,
                'response_time': response_time
            }
        )
        
        self.log_event(event)
    
    # Métodos de análisis y reporting
    
    def get_security_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Obtener resumen de seguridad"""
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            # Leer logs de auditoría recientes
            security_events = self._parse_audit_logs(start_time, end_time, 
                                                   categories=[AuditCategory.SECURITY])
            
            auth_failures = self._parse_audit_logs(start_time, end_time,
                                                 event_types=['login_failed', 'invalid_token'])
            
            suspicious_activities = self._detect_suspicious_activities(start_time, end_time)
            
            return {
                'period': {
                    'start': start_time.isoformat(),
                    'end': end_time.isoformat(),
                    'hours': hours
                },
                'security_events': len(security_events),
                'auth_failures': len(auth_failures),
                'suspicious_activities': suspicious_activities,
                'top_failed_ips': self._get_top_failed_ips(auth_failures),
                'recommendations': self._generate_security_recommendations(security_events, auth_failures)
            }
            
        except Exception as e:
            logger.error(f"Error generating security summary: {str(e)}")
            return {'error': str(e)}
    
    def _parse_audit_logs(self, start_time: datetime, end_time: datetime,
                         categories: Optional[List[str]] = None,
                         event_types: Optional[List[str]] = None) -> List[Dict]:
        """Parsear logs de auditoría"""
        events = []
        try:
            with open('logs/audit.log', 'r', encoding='utf-8') as f:
                for line in f:
                    if 'AUDIT:' in line:
                        try:
                            # Extraer JSON del log
                            json_start = line.find('{')
                            if json_start != -1:
                                event_data = json.loads(line[json_start:])
                                event_time = datetime.fromisoformat(event_data['timestamp'])
                                
                                # Filtrar por tiempo
                                if start_time <= event_time <= end_time:
                                    # Filtrar por categoría
                                    if categories and event_data.get('category') not in categories:
                                        continue
                                    
                                    # Filtrar por tipo de evento
                                    if event_types and event_data.get('event_type') not in event_types:
                                        continue
                                    
                                    events.append(event_data)
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            logger.warning("Audit log file not found")
        
        return events
    
    def _detect_suspicious_activities(self, start_time: datetime, end_time: datetime) -> List[Dict]:
        """Detectar actividades sospechosas"""
        suspicious = []
        
        # Múltiples intentos de login fallidos
        failed_logins = self._parse_audit_logs(start_time, end_time, 
                                             event_types=['login_failed'])
        
        # Agrupar por IP
        ip_failures = {}
        for event in failed_logins:
            ip = event.get('ip_address', 'unknown')
            if ip not in ip_failures:
                ip_failures[ip] = 0
            ip_failures[ip] += 1
        
        # IPs con más de 5 intentos fallidos
        for ip, count in ip_failures.items():
            if count >= 5:
                suspicious.append({
                    'type': 'multiple_login_failures',
                    'ip_address': ip,
                    'count': count,
                    'severity': 'high' if count >= 10 else 'medium'
                })
        
        return suspicious
    
    def _get_top_failed_ips(self, failed_events: List[Dict]) -> List[Dict]:
        """Obtener IPs con más intentos fallidos"""
        ip_counts = {}
        for event in failed_events:
            ip = event.get('ip_address', 'unknown')
            if ip not in ip_counts:
                ip_counts[ip] = 0
            ip_counts[ip] += 1
        
        # Ordenar por cantidad de intentos
        sorted_ips = sorted(ip_counts.items(), key=lambda x: x[1], reverse=True)
        
        return [{'ip': ip, 'failures': count} for ip, count in sorted_ips[:10]]
    
    def _generate_security_recommendations(self, security_events: List[Dict], 
                                         auth_failures: List[Dict]) -> List[str]:
        """Generar recomendaciones de seguridad"""
        recommendations = []
        
        if len(auth_failures) > 10:
            recommendations.append("Considerar implementar rate limiting más estricto para login")
        
        if len(security_events) > 5:
            recommendations.append("Revisar eventos de seguridad recientes")
        
        # Verificar si hay muchos accesos desde IPs diferentes
        unique_ips = len(set(event.get('ip_address') for event in auth_failures))
        if unique_ips > 5:
            recommendations.append("Actividad desde múltiples IPs - verificar si es normal")
        
        return recommendations

# Instancia global del servicio
audit_service = AuditService()

# Decorador para auditoría automática
def audit_action(event_type: str, category: str = AuditCategory.SYSTEM, 
                level: str = AuditLevel.INFO):
    """Decorador para auditoría automática de funciones"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            user_id = None
            
            try:
                # Intentar obtener user_id del JWT
                try:
                    user_id = get_jwt_identity()
                except:
                    pass
                
                # Ejecutar función
                result = func(*args, **kwargs)
                
                # Log exitoso
                audit_service.log_event(AuditEvent(
                    event_type=event_type,
                    category=category,
                    level=level,
                    user_id=user_id,
                    description=f"Function {func.__name__} executed successfully",
                    details={
                        'function': func.__name__,
                        'execution_time': (datetime.now() - start_time).total_seconds()
                    }
                ))
                
                return result
                
            except Exception as e:
                # Log error
                audit_service.log_event(AuditEvent(
                    event_type=f"{event_type}_failed",
                    category=category,
                    level=AuditLevel.ERROR,
                    user_id=user_id,
                    description=f"Function {func.__name__} failed: {str(e)}",
                    details={
                        'function': func.__name__,
                        'error': str(e),
                        'execution_time': (datetime.now() - start_time).total_seconds()
                    }
                ))
                raise
        
        return wrapper
    return decorator
