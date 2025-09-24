"""
Rutas de Autenticación API v1 - Versión Empresarial con Validación Robusta
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from datetime import timedelta
import logging

from app.core.exceptions import AuthenticationException, ValidationException, handle_errors
from app.core.validators import validate_json, UserValidationSchema, SecurityValidator
from app.core.metrics import app_metrics, track_execution_time, count_calls
from app.core.logging_config import LoggerUtils

logger = logging.getLogger('security')

# Crear blueprint
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['POST'])
@handle_errors
@track_execution_time('auth_login_duration')
@count_calls('auth_login_attempts')
def login():
    """
    Autenticación empresarial de usuario con validación robusta
    
    Body:
    {
        "username": "admin",
        "password": "admin"
    }
    """
    # Validación de entrada
    data = request.get_json()
    if not data:
        raise ValidationException("Se requiere contenido JSON válido")
    
    username = data.get('username', '').strip()
    password = data.get('password', '')
    
    if not username or not password:
        raise ValidationException("Se requieren username y password")
    
    # Validación de seguridad
    username = SecurityValidator.validate_safe_input(username, 'username')
    
    # Log de intento de autenticación
    LoggerUtils.log_security_event(
        'login_attempt',
        {
            'username': username,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', 'Unknown')
        }
    )
    
    # Validación de credenciales (en producción usar base de datos con hash)
    if username == 'admin' and password == 'admin':
        # Crear tokens con información adicional
        additional_claims = {
            'role': 'admin',
            'permissions': ['read:all', 'write:all', 'admin:all'],
            'ip_address': request.remote_addr
        }
        
        access_token = create_access_token(
            identity=username,
            expires_delta=timedelta(hours=1),
            additional_claims=additional_claims
        )
        refresh_token = create_refresh_token(
            identity=username,
            expires_delta=timedelta(days=30)
        )
        
        # Log de login exitoso
        LoggerUtils.log_security_event(
            'login_success',
            {
                'username': username,
                'ip_address': request.remote_addr,
                'role': 'admin'
            },
            level='INFO'
        )
        
        # Registrar métricas
        app_metrics.record_authentication_attempt(True)
        
        return jsonify({
            'success': True,
            'message': 'Autenticación exitosa',
            'data': {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user': {
                    'username': username,
                    'role': 'admin',
                    'permissions': additional_claims['permissions']
                },
                'expires_in': 3600  # 1 hora en segundos
            }
        }), 200
    else:
        # Log de login fallido
        LoggerUtils.log_security_event(
            'login_failure',
            {
                'username': username,
                'ip_address': request.remote_addr,
                'reason': 'invalid_credentials'
            },
            level='WARNING'
        )
        
        # Registrar métricas
        app_metrics.record_authentication_attempt(False)
        
        raise AuthenticationException("Credenciales inválidas")

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Renovar token de acceso"""
    try:
        current_user = get_jwt_identity()
        new_token = create_access_token(
            identity=current_user,
            expires_delta=timedelta(hours=1)
        )
        
        return jsonify({
            'access_token': new_token
        }), 200
        
    except Exception as e:
        logger.error(f'Error renovando token: {e}')
        return jsonify({
            'error': 'Error renovando token'
        }), 500

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Cerrar sesión"""
    try:
        current_user = get_jwt_identity()
        logger.info(f'Logout para usuario: {current_user}')
        
        return jsonify({
            'message': 'Logout exitoso'
        }), 200
        
    except Exception as e:
        logger.error(f'Error en logout: {e}')
        return jsonify({
            'error': 'Error en logout'
        }), 500

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Obtener perfil del usuario actual"""
    try:
        current_user = get_jwt_identity()
        
        return jsonify({
            'user': {
                'username': current_user,
                'role': 'admin',
                'permissions': [
                    'read:products',
                    'write:products',
                    'read:sales',
                    'write:sales',
                    'read:inventory',
                    'write:inventory',
                    'admin:all'
                ]
            }
        }), 200
        
    except Exception as e:
        logger.error(f'Error obteniendo perfil: {e}')
        return jsonify({
            'error': 'Error obteniendo perfil'
        }), 500

@bp.route('/validate', methods=['GET'])
@jwt_required()
def validate_token():
    """Validar token actual"""
    try:
        current_user = get_jwt_identity()
        
        return jsonify({
            'valid': True,
            'user': current_user,
            'message': 'Token válido'
        }), 200
        
    except Exception as e:
        logger.error(f'Error validando token: {e}')
        return jsonify({
            'error': 'Token inválido'
        }), 401
