"""
Users API v1 - Sistema POS O'Data
================================
Endpoints de usuarios con validaciones enterprise.
"""

from flask import Blueprint, request, jsonify  # type: ignore[import]
from app.container import container
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.exceptions import ValidationError, AuthenticationError
import logging
from app.security.jwt_utils import create_access_token, create_refresh_token, decode_token

logger = logging.getLogger(__name__)

# Crear blueprint
users_bp = Blueprint('users', __name__)

@users_bp.route('/users', methods=['POST'])
def create_user():
    """Crear nuevo usuario"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("Request body is required")
        
        # Obtener servicio del container
        user_repository = container.get(UserRepository)
        user_service = UserService(user_repository)
        
        # Crear usuario
        user = user_service.create_user(data)
        
        logger.info(f"User created: {user['username']}", extra={
            'user_id': user['id'],
            'username': user['username']
        })
        
        return jsonify({
            'status': 'success',
            'data': user,
            'message': 'User created successfully'
        }), 201
        
    except ValidationError as e:
        logger.warning(f"Validation error in create_user: {e.message}", extra={
            'field': getattr(e, 'field', None),
            'context': e.context
        })
        return jsonify(e.to_dict()), e.status_code
    
    except Exception as e:
        logger.error(f"Unexpected error in create_user: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@users_bp.route('/users', methods=['GET'])

def get_users():
    """Obtener lista de usuarios"""
    try:
        # Obtener parámetros de paginación
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        
        # Obtener filtros
        is_active = request.args.get('is_active', type=bool)
        role = request.args.get('role')
        
        # Obtener servicio
        user_repository = container.get(UserRepository)
        user_service = UserService(user_repository)
        
        # Aplicar filtros
        filters = {}
        if is_active is not None:
            filters['is_active'] = is_active
        if role:
            filters['role'] = role
        
        # Obtener usuarios
        result = user_service.get_users(page=page, per_page=per_page, **filters)
        
        return jsonify({
            'status': 'success',
            'data': result
        })
        
    except Exception as e:
        logger.error(f"Error in get_users: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@users_bp.route('/users/<int:user_id>', methods=['GET'])

def get_user(user_id):
    """Obtener usuario por ID"""
    try:
        # Obtener servicio
        user_repository = container.get(UserRepository)
        user_service = UserService(user_repository)
        
        # Obtener usuario
        user = user_service.get_user(user_id)
        
        return jsonify({
            'status': 'success',
            'data': user
        })
        
    except Exception as e:
        logger.error(f"Error in get_user: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@users_bp.route('/users/stats', methods=['GET'])

def get_user_stats():
    """Obtener estadísticas de usuarios"""
    try:
        # Obtener servicio
        user_repository = container.get(UserRepository)
        user_service = UserService(user_repository)
        
        # Obtener estadísticas
        stats = user_service.get_user_stats()
        
        return jsonify({
            'status': 'success',
            'data': stats
        })
        
    except Exception as e:
        logger.error(f"Error in get_user_stats: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

# --- Simple Auth ---
@users_bp.route('/auth/login', methods=['POST'])

def login():
    """Login básico: verifica credenciales y devuelve rol y token simple"""
    try:
        data = request.get_json() or {}
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            raise ValidationError("username and password are required")

        # Servicio de usuarios
        user_repository = container.get(UserRepository)
        user_service = UserService(user_repository)

        # Buscar usuario por username
        user = user_service.get_user_by_username(username)
        if not user:
            raise AuthenticationError("Invalid credentials")

        # Verificar contraseña
        if not user.check_password(password):
            raise AuthenticationError("Invalid credentials")

        # Actualizar last_login
        user.update_last_login()

        # Rol efectivo: usa primary_role si existe
        primary_role = getattr(user, "primary_role", None)
        effective_role = primary_role.name if primary_role else user.role

        # Emitir JWT access y refresh
        access = create_access_token(identity=user.username, role=effective_role)
        refresh = create_refresh_token(identity=user.username)

        return jsonify({
            'status': 'success',
            'data': {
                'username': user.username,
                'role': effective_role,
                'access_token': access,
                'refresh_token': refresh
            },
            'message': 'Login successful'
        })
    except ValidationError as e:
        return jsonify(e.to_dict()), e.status_code
    except AuthenticationError as e:
        return jsonify({'error': {'code': 'AUTH_FAILED', 'message': e.message}}), 401
    except Exception as e:
        logger.error(f"Unexpected error in login: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@users_bp.route('/auth/refresh', methods=['POST'])

def refresh():
    try:
        data = request.get_json() or {}
        token = data.get('refresh_token')
        if not token:
            raise ValidationError('refresh_token is required')
        payload = decode_token(token)
        if payload.get('type') != 'refresh':
            raise AuthenticationError('Invalid token type')
        username = payload.get('sub')
        # Reemitir access
        access = create_access_token(identity=username, role=data.get('role', 'cashier'))
        return jsonify({'status': 'success', 'data': {'access_token': access}})
    except ValidationError as e:
        return jsonify(e.to_dict()), e.status_code
    except Exception as e:
        logger.error(f"Error in refresh: {str(e)}")
        return jsonify({'error': {'code': 'INVALID_TOKEN', 'message': 'Invalid or expired token'}}), 401
