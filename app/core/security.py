import re
import hashlib
import secrets
import time
from typing import Dict, Any, Optional, List
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
import redis
import logging

logger = logging.getLogger(__name__)

class SecurityManager:
    """Gestor de seguridad del sistema"""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        self.redis = redis_client
        self.rate_limit_window = 60  # segundos
        self.max_requests_per_window = 100
        
        # Patrones de validación
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.password_pattern = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$')
        # Patrón mejorado para SQL injection que incluye OR, AND, comentarios y comillas
        self.sql_injection_pattern = re.compile(r'(\b(union|select|insert|update|delete|drop|create|alter|or|and)\b|\'|\-\-|\/\*|\*\/)', re.IGNORECASE)
        self.xss_pattern = re.compile(r'<script|javascript:|vbscript:|onload=|onerror=', re.IGNORECASE)
        
        # Lista de IPs bloqueadas
        self.blocked_ips = set()
        
        # Configuración de seguridad
        self.security_config = {
            'max_login_attempts': 5,
            'lockout_duration': 900,  # 15 minutos
            'session_timeout': 3600,  # 1 hora
            'password_min_length': 8,
            'require_special_chars': True,
            'max_concurrent_sessions': 3
        }
    
    def validate_input(self, data: Dict[str, Any], rules: Dict[str, Any]) -> Dict[str, Any]:
        """Valida datos de entrada según reglas específicas"""
        errors = []
        sanitized_data = {}
        
        for field, rule in rules.items():
            value = data.get(field)
            
            # Validar campo requerido
            if rule.get('required', False) and not value:
                errors.append(f"El campo '{field}' es requerido")
                continue
            
            if value is not None:
                # Validar tipo de dato
                if 'type' in rule:
                    if not isinstance(value, rule['type']):
                        errors.append(f"El campo '{field}' debe ser de tipo {rule['type'].__name__}")
                        continue
                
                # Validar longitud
                if 'min_length' in rule and len(str(value)) < rule['min_length']:
                    errors.append(f"El campo '{field}' debe tener al menos {rule['min_length']} caracteres")
                
                if 'max_length' in rule and len(str(value)) > rule['max_length']:
                    errors.append(f"El campo '{field}' debe tener máximo {rule['max_length']} caracteres")
                
                # Validar patrón
                if 'pattern' in rule:
                    if not re.match(rule['pattern'], str(value)):
                        errors.append(f"El campo '{field}' no cumple con el formato requerido")
                
                # Validar rango
                if 'min_value' in rule and value < rule['min_value']:
                    errors.append(f"El campo '{field}' debe ser mayor a {rule['min_value']}")
                
                if 'max_value' in rule and value > rule['max_value']:
                    errors.append(f"El campo '{field}' debe ser menor a {rule['max_value']}")
                
                # Sanitizar valor
                sanitized_value = self.sanitize_input(value)
                sanitized_data[field] = sanitized_value
        
        if errors:
            return {'valid': False, 'errors': errors}
        
        return {'valid': True, 'data': sanitized_data}
    
    def sanitize_input(self, value: Any) -> Any:
        """Sanitiza datos de entrada"""
        if isinstance(value, str):
            # Remover caracteres peligrosos
            value = value.strip()
            value = re.sub(r'<script.*?</script>', '', value, flags=re.IGNORECASE)
            value = re.sub(r'javascript:', '', value, flags=re.IGNORECASE)
            value = re.sub(r'vbscript:', '', value, flags=re.IGNORECASE)
            value = re.sub(r'on\w+\s*=', '', value, flags=re.IGNORECASE)
            
            # Escapar caracteres especiales
            value = value.replace("'", "''")
            value = value.replace('"', '""')
            value = value.replace('\\', '\\\\')
        
        return value
    
    def check_sql_injection(self, query: str) -> bool:
        """Detecta intentos de SQL injection"""
        return bool(self.sql_injection_pattern.search(query))
    
    def check_xss_attack(self, content: str) -> bool:
        """Detecta intentos de XSS"""
        return bool(self.xss_pattern.search(content))
    
    def validate_password(self, password: str) -> Dict[str, Any]:
        """Valida fortaleza de contraseña"""
        errors = []
        
        if len(password) < self.security_config['password_min_length']:
            errors.append(f"La contraseña debe tener al menos {self.security_config['password_min_length']} caracteres")
        
        if not re.search(r'[a-z]', password):
            errors.append("La contraseña debe contener al menos una letra minúscula")
        
        if not re.search(r'[A-Z]', password):
            errors.append("La contraseña debe contener al menos una letra mayúscula")
        
        if not re.search(r'\d', password):
            errors.append("La contraseña debe contener al menos un número")
        
        if self.security_config['require_special_chars']:
            if not re.search(r'[@$!%*?&]', password):
                errors.append("La contraseña debe contener al menos un carácter especial (@$!%*?&)")
        
        # Verificar contraseñas comunes
        common_passwords = ['password', '123456', 'admin', 'qwerty', 'letmein']
        if password.lower() in common_passwords:
            errors.append("La contraseña es demasiado común")
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'strength': self.calculate_password_strength(password)
        }
    
    def calculate_password_strength(self, password: str) -> str:
        """Calcula la fortaleza de una contraseña"""
        score = 0
        
        # Longitud
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        
        # Complejidad
        if re.search(r'[a-z]', password):
            score += 1
        if re.search(r'[A-Z]', password):
            score += 1
        if re.search(r'\d', password):
            score += 1
        if re.search(r'[@$!%*?&]', password):
            score += 1
        
        # Variedad de caracteres
        unique_chars = len(set(password))
        if unique_chars >= 8:
            score += 1
        
        if score <= 2:
            return 'débil'
        elif score <= 4:
            return 'media'
        elif score <= 6:
            return 'fuerte'
        else:
            return 'muy fuerte'
    
    def hash_password(self, password: str) -> str:
        """Genera hash seguro de contraseña"""
        salt = secrets.token_hex(16)
        hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}${hash_obj.hex()}"
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verifica contraseña contra hash"""
        try:
            salt, hash_hex = hashed_password.split('$')
            hash_obj = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return hash_obj.hex() == hash_hex
        except:
            return False
    
    def check_rate_limit(self, identifier: str, limit: int = None) -> bool:
        """Verifica rate limiting"""
        if limit is None:
            limit = self.max_requests_per_window
        
        current_time = int(time.time())
        window_start = current_time - self.rate_limit_window
        
        # Usar Redis para tracking
        key = f"rate_limit:{identifier}"
        
        # Obtener requests en la ventana actual
        requests = self.redis.zrangebyscore(key, window_start, current_time)
        
        if len(requests) >= limit:
            return False
        
        # Agregar request actual
        self.redis.zadd(key, {str(current_time): current_time})
        self.redis.expire(key, self.rate_limit_window)
        
        return True
    
    def check_login_attempts(self, username: str) -> Dict[str, Any]:
        """Verifica intentos de login"""
        key = f"login_attempts:{username}"
        attempts = self.redis.get(key)
        
        if attempts:
            attempts = int(attempts)
            if attempts >= self.security_config['max_login_attempts']:
                return {
                    'blocked': True,
                    'remaining_time': self.redis.ttl(key),
                    'message': 'Cuenta bloqueada por múltiples intentos fallidos'
                }
        
        return {'blocked': False}
    
    def record_login_attempt(self, username: str, success: bool):
        """Registra intento de login"""
        key = f"login_attempts:{username}"
        
        if success:
            # Resetear intentos en login exitoso
            self.redis.delete(key)
        else:
            # Incrementar intentos fallidos
            attempts = self.redis.incr(key)
            if attempts == 1:
                # Establecer expiración en el primer intento
                self.redis.expire(key, self.security_config['lockout_duration'])
    
    def check_ip_blocklist(self, ip: str) -> bool:
        """Verifica si IP está bloqueada"""
        return ip in self.blocked_ips
    
    def block_ip(self, ip: str, duration: int = 3600):
        """Bloquea IP por duración específica"""
        self.blocked_ips.add(ip)
        # Programar desbloqueo
        current_app.scheduler.add_job(
            func=self.unblock_ip,
            trigger='date',
            run_date=time.time() + duration,
            args=[ip]
        )
    
    def unblock_ip(self, ip: str):
        """Desbloquea IP"""
        self.blocked_ips.discard(ip)
    
    def generate_secure_token(self, length: int = 32) -> str:
        """Genera token seguro"""
        return secrets.token_urlsafe(length)
    
    def validate_session(self, session_id: str) -> bool:
        """Valida sesión de usuario"""
        key = f"session:{session_id}"
        return bool(self.redis.exists(key))
    
    def create_session(self, user_id: int, session_id: str):
        """Crea nueva sesión"""
        key = f"session:{session_id}"
        self.redis.setex(key, self.security_config['session_timeout'], user_id)
    
    def destroy_session(self, session_id: str):
        """Destruye sesión"""
        key = f"session:{session_id}"
        self.redis.delete(key)
    
    def check_concurrent_sessions(self, user_id: int) -> bool:
        """Verifica límite de sesiones concurrentes"""
        pattern = f"session:*"
        sessions = self.redis.keys(pattern)
        
        user_sessions = 0
        for session_key in sessions:
            if self.redis.get(session_key) == str(user_id):
                user_sessions += 1
        
        return user_sessions < self.security_config['max_concurrent_sessions']
    
    def log_security_event(self, event_type: str, details: Dict[str, Any]):
        """Registra evento de seguridad"""
        log_entry = {
            'timestamp': time.time(),
            'event_type': event_type,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent'),
            'details': details
        }
        
        logger.warning(f"Security Event: {event_type} - {details}")
        
        # Almacenar en Redis para análisis
        self.redis.lpush('security_logs', str(log_entry))
        self.redis.ltrim('security_logs', 0, 999)  # Mantener solo últimos 1000 eventos

# Decoradores de seguridad
def require_auth(f):
    """Decorador para requerir autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except:
            return jsonify({'error': 'Token de autenticación requerido'}), 401
    return decorated_function

def require_role(roles: List[str]):
    """Decorador para requerir roles específicos"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user = get_jwt_identity()
                
                # Verificar rol del usuario
                if current_user.get('role') not in roles:
                    return jsonify({'error': 'Permisos insuficientes'}), 403
                
                return f(*args, **kwargs)
            except:
                return jsonify({'error': 'Token de autenticación requerido'}), 401
        return decorated_function
    return decorator

def rate_limit(limit: int = 100, window: int = 60):
    """Decorador para rate limiting"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            security_manager = current_app.security_manager
            identifier = request.remote_addr
            
            if not security_manager.check_rate_limit(identifier, limit):
                return jsonify({
                    'error': 'Rate limit excedido',
                    'retry_after': window
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_input(rules: Dict[str, Any]):
    """Decorador para validar entrada"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            security_manager = current_app.security_manager
            
            # Obtener datos de entrada
            if request.method == 'GET':
                data = request.args.to_dict()
            else:
                data = request.get_json() or {}
            
            # Validar datos
            validation_result = security_manager.validate_input(data, rules)
            
            if not validation_result['valid']:
                return jsonify({
                    'error': 'Datos de entrada inválidos',
                    'details': validation_result['errors']
                }), 400
            
            # Pasar datos sanitizados a la función
            kwargs['validated_data'] = validation_result['data']
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_security_events(event_type: str):
    """Decorador para logging de eventos de seguridad"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            security_manager = current_app.security_manager
            
            # Log del evento
            security_manager.log_security_event(event_type, {
                'endpoint': request.endpoint,
                'method': request.method,
                'ip': request.remote_addr
            })
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Instancia global del gestor de seguridad
security_manager = None

def init_security(app):
    """Inicializa el gestor de seguridad"""
    global security_manager
    try:
        # Intentar usar Redis si está disponible
        if hasattr(app, 'redis') and app.redis:
            security_manager = SecurityManager(app.redis)
        else:
            # Usar modo sin Redis
            security_manager = SecurityManager(None)
        app.security_manager = security_manager
    except Exception as e:
        app.logger.warning(f"Error inicializando seguridad: {e}. Usando modo básico.")
        security_manager = SecurityManager(None)
        app.security_manager = security_manager 