"""
Módulo de Rate Limiting condicional para el Sistema POS Odata
Funciona con o sin flask-limiter instalado
"""

import functools
from flask import current_app, request, jsonify
import time
import hashlib

def conditional_rate_limit(limit_string):
    """
    Decorador de rate limiting que funciona condicionalmente
    
    Args:
        limit_string (str): String de límite (ej: "10 per minute")
    
    Returns:
        function: Decorador que aplica rate limiting si está disponible
    """
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar si flask-limiter está disponible
            if hasattr(current_app, 'limiter') and current_app.limiter is not None:
                # Usar flask-limiter si está disponible
                try:
                    # Aplicar el límite usando flask-limiter
                    return current_app.limiter.limit(limit_string)(f)(*args, **kwargs)
                except Exception as e:
                    current_app.logger.warning(f"Error en rate limiting: {e}")
                    # Continuar sin rate limiting si hay error
                    return f(*args, **kwargs)
            else:
                # Implementación básica de rate limiting usando Redis
                try:
                    if _check_basic_rate_limit(limit_string):
                        return f(*args, **kwargs)
                    else:
                        return jsonify({
                            'error': 'Rate limit exceeded',
                            'message': f'Too many requests. Limit: {limit_string}'
                        }), 429
                except Exception as e:
                    current_app.logger.warning(f"Error en rate limiting básico: {e}")
                    # Continuar sin rate limiting si hay error
                    return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def _check_basic_rate_limit(limit_string):
    """
    Implementación básica de rate limiting usando Redis
    
    Args:
        limit_string (str): String de límite (ej: "10 per minute")
    
    Returns:
        bool: True si la solicitud está permitida, False si excede el límite
    """
    try:
        # Parsear el límite
        parts = limit_string.split()
        if len(parts) != 3:
            return True  # Si no se puede parsear, permitir
        
        max_requests = int(parts[0])
        time_unit = parts[1]
        period = parts[2]
        
        # Convertir a segundos
        if period == 'second':
            window = 1
        elif period == 'minute':
            window = 60
        elif period == 'hour':
            window = 3600
        elif period == 'day':
            window = 86400
        else:
            return True  # Período no reconocido, permitir
        
        # Generar clave única para el cliente
        client_ip = request.remote_addr
        key = f"rate_limit:{client_ip}:{f.__name__}"
        
        # Verificar límite usando Redis
        redis_client = current_app.redis
        current_time = int(time.time())
        window_start = current_time - (current_time % window)
        
        # Obtener solicitudes en la ventana actual
        requests_in_window = redis_client.get(f"{key}:{window_start}")
        
        if requests_in_window is None:
            # Primera solicitud en esta ventana
            redis_client.setex(f"{key}:{window_start}", window, 1)
            return True
        else:
            current_requests = int(requests_in_window)
            if current_requests < max_requests:
                # Incrementar contador
                redis_client.incr(f"{key}:{window_start}")
                return True
            else:
                # Límite excedido
                return False
                
    except Exception as e:
        current_app.logger.error(f"Error en rate limiting básico: {e}")
        return True  # En caso de error, permitir la solicitud

def rate_limit_10_per_minute(f):
    """Decorador para límite de 10 solicitudes por minuto"""
    return conditional_rate_limit("10 per minute")(f)

def rate_limit_100_per_hour(f):
    """Decorador para límite de 100 solicitudes por hora"""
    return conditional_rate_limit("100 per hour")(f)

def rate_limit_1000_per_day(f):
    """Decorador para límite de 1000 solicitudes por día"""
    return conditional_rate_limit("1000 per day")(f)
