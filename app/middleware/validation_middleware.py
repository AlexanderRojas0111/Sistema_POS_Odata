"""
Middleware de Validación - Sistema POS O'Data
============================================
Middleware para validar datos de entrada usando esquemas Marshmallow
"""

from functools import wraps
from flask import request, jsonify, current_app
from marshmallow import ValidationError
import logging

logger = logging.getLogger(__name__)

def validate_request(schema, location='json'):
    """
    Decorator para validar datos de entrada
    
    Args:
        schema: Esquema de validación Marshmallow
        location: Ubicación de los datos ('json', 'form', 'query', 'args')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Obtener datos según la ubicación
                if location == 'json':
                    data = request.get_json()
                elif location == 'form':
                    data = request.form.to_dict()
                elif location == 'query':
                    data = request.args.to_dict()
                elif location == 'args':
                    data = request.args.to_dict()
                else:
                    data = request.get_json()
                
                # Validar datos
                validated_data = schema.load(data)
                
                # Agregar datos validados al contexto de la request
                request.validated_data = validated_data
                
                return f(*args, **kwargs)
                
            except ValidationError as e:
                logger.warning(f"Validation error in {f.__name__}: {e.messages}")
                return jsonify({
                    'success': False,
                    'message': 'Datos de entrada no válidos',
                    'errors': e.messages
                }), 400
                
            except Exception as e:
                logger.error(f"Unexpected error in validation middleware: {str(e)}")
                return jsonify({
                    'success': False,
                    'message': 'Error interno del servidor',
                    'error': 'validation_error'
                }), 500
                
        return decorated_function
    return decorator

def validate_query_params(schema):
    """
    Decorator específico para validar parámetros de consulta
    """
    return validate_request(schema, location='query')

def validate_form_data(schema):
    """
    Decorator específico para validar datos de formulario
    """
    return validate_request(schema, location='form')

def validate_json_data(schema):
    """
    Decorator específico para validar datos JSON
    """
    return validate_request(schema, location='json')

class ValidationMiddleware:
    """Middleware de validación para la aplicación"""
    
    def __init__(self, app=None):
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar middleware con la aplicación Flask"""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Ejecutar antes de cada request"""
        # Log de request para debugging
        if current_app.debug:
            logger.debug(f"Request: {request.method} {request.path}")
            logger.debug(f"Headers: {dict(request.headers)}")
            if request.get_json():
                logger.debug(f"JSON Data: {request.get_json()}")
    
    def after_request(self, response):
        """Ejecutar después de cada request"""
        # Log de response para debugging
        if current_app.debug:
            logger.debug(f"Response: {response.status_code}")
        
        # Agregar headers de seguridad adicionales
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        
        return response

def handle_validation_errors(error):
    """Manejador global de errores de validación"""
    logger.error(f"Global validation error: {str(error)}")
    return jsonify({
        'success': False,
        'message': 'Error de validación',
        'error': str(error)
    }), 400

def sanitize_input(data):
    """
    Sanitizar datos de entrada para prevenir inyecciones
    
    Args:
        data: Datos a sanitizar (dict, list, o string)
    
    Returns:
        Datos sanitizados
    """
    if isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    elif isinstance(data, str):
        # Remover caracteres peligrosos
        dangerous_chars = ['<', '>', '"', "'", '&', ';', '(', ')', '|', '`', '$']
        for char in dangerous_chars:
            data = data.replace(char, '')
        return data.strip()
    else:
        return data

def validate_file_upload(allowed_extensions=None, max_size=None):
    """
    Decorator para validar subida de archivos
    
    Args:
        allowed_extensions: Lista de extensiones permitidas
        max_size: Tamaño máximo en bytes
    """
    if allowed_extensions is None:
        allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf']
    
    if max_size is None:
        max_size = 5 * 1024 * 1024  # 5MB por defecto
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'file' not in request.files:
                return jsonify({
                    'success': False,
                    'message': 'No se encontró archivo'
                }), 400
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({
                    'success': False,
                    'message': 'No se seleccionó archivo'
                }), 400
            
            # Validar extensión
            if not any(file.filename.lower().endswith(ext) for ext in allowed_extensions):
                return jsonify({
                    'success': False,
                    'message': f'Extensión no permitida. Permitidas: {", ".join(allowed_extensions)}'
                }), 400
            
            # Validar tamaño
            file.seek(0, 2)  # Ir al final del archivo
            file_size = file.tell()
            file.seek(0)  # Volver al inicio
            
            if file_size > max_size:
                return jsonify({
                    'success': False,
                    'message': f'Archivo demasiado grande. Máximo: {max_size // (1024*1024)}MB'
                }), 400
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

# Instancia del middleware
validation_middleware = ValidationMiddleware()
