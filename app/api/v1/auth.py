"""
Authentication API v1 - Sistema POS O'Data
==========================================
Endpoints de autenticación JWT.
"""

from flask import Blueprint, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.container import container
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.exceptions import ValidationError, AuthenticationError
from app.security.jwt_utils import create_access_token, create_refresh_token, decode_token
import logging

logger = logging.getLogger(__name__)

# Crear blueprint
auth_bp = Blueprint('auth', __name__)

# Configurar rate limiting
limiter = Limiter(key_func=get_remote_address)

@auth_bp.route('/auth/test', methods=['GET'])
def auth_test():
    """Endpoint de test para verificar routing"""
    logger.info("AUTH TEST ENDPOINT CALLED!")
    return jsonify({"status": "auth_test_working", "message": "Auth blueprint routing works"})

@auth_bp.route('/auth/login', methods=['POST'])
# @limiter.limit("20 per minute")  # TEMPORALMENTE DESHABILITADO PARA DEBUG
def login():
    """Login JWT: verifica credenciales y devuelve tokens de acceso y refresh"""
    try:
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')
        
        # DEBUG LOGGING
        logger.info(f"LOGIN ATTEMPT - Username: {username}, Password length: {len(password) if password else 0}")
        
        if not username or not password:
            logger.info("LOGIN FAILED - Missing credentials")
            raise ValidationError("username and password are required")

        # Servicio de usuarios
        user_repository = container.get(UserRepository)
        user_service = UserService(user_repository)
        logger.info(f"LOGIN DEBUG - Container and service created")

        # Buscar usuario por username
        user = user_service.get_user_by_username(username)
        logger.info(f"LOGIN DEBUG - User found: {user is not None}")
        if user:
            logger.info(f"LOGIN DEBUG - User details: {user.username}, {user.email}, {user.role}, active: {user.is_active}")
        
        if not user:
            logger.info("LOGIN FAILED - User not found")
            raise AuthenticationError("Invalid credentials")

        # Verificar contraseña
        password_check = user.check_password(password)
        logger.info(f"LOGIN DEBUG - Password check result: {password_check}")
        if not password_check:
            logger.info("LOGIN FAILED - Password check failed")
            raise AuthenticationError("Invalid credentials")

        # Actualizar last_login
        user.update_last_login()

        # Emitir JWT access y refresh
        access = create_access_token(identity=user.username, role=user.role)
        refresh = create_refresh_token(identity=user.username)

        logger.info(f"Successful login for user: {user.username}")

        return jsonify({
            'status': 'success',
            'data': {
                'user_id': user.id,  # Agregar ID numérico del usuario
                'username': user.username,
                'role': user.role,
                'access_token': access,
                'refresh_token': refresh
            },
            'message': 'Login successful'
        })
        
    except ValidationError as e:
        logger.warning(f"Validation error in login: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    except AuthenticationError as e:
        logger.warning(f"Authentication failed for username: {username}")
        return jsonify({'error': {'code': 'AUTH_FAILED', 'message': e.message}}), 401
    except Exception as e:
        logger.error(f"Unexpected error in login: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@auth_bp.route('/auth/refresh', methods=['POST'])
@limiter.limit("30 per minute")
def refresh():
    """Refresh JWT: genera nuevo token de acceso usando refresh token"""
    try:
        data = request.get_json() or {}
        token = data.get('refresh_token')
        
        if not token:
            raise ValidationError('refresh_token is required')
            
        payload = decode_token(token)
        if payload.get('type') != 'refresh':
            raise AuthenticationError('Invalid token type')
            
        username = payload.get('sub')
        if not username:
            raise AuthenticationError('Invalid token payload')
        
        # Obtener rol del usuario actual
        user_repository = container.get(UserRepository)
        user_service = UserService(user_repository)
        user = user_service.get_user_by_username(username)
        
        if not user:
            raise AuthenticationError('User not found')
        
        # Reemitir access token
        access = create_access_token(identity=username, role=user.role)
        
        logger.info(f"Token refreshed for user: {username}")
        
        return jsonify({
            'status': 'success', 
            'data': {
                'access_token': access
            }
        })
        
    except ValidationError as e:
        logger.warning(f"Validation error in refresh: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    except AuthenticationError as e:
        logger.warning(f"Authentication error in refresh: {e.message}")
        return jsonify({'error': {'code': 'INVALID_TOKEN', 'message': e.message}}), 401
    except Exception as e:
        logger.error(f"Error in refresh: {str(e)}")
        return jsonify({'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid or expired token'}}), 401
