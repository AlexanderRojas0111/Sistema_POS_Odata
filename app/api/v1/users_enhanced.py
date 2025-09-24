"""
Users API Enhanced - Sistema POS O'Data
======================================
Endpoints de usuarios con validaciones y respuestas consistentes.
"""

from flask import Blueprint, request
from app.container import container
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.utils.response_helpers import (
    success_response, error_response, created_response, 
    updated_response, not_found_response, paginated_response,
    unauthorized_response
)
from app.schemas.validation_schemas import user_schema, login_schema
from app.middleware.validation_middleware import validate_json_data
from app.middleware.error_handler_enhanced import error_handler
import logging

logger = logging.getLogger(__name__)

# Crear blueprint
users_enhanced_bp = Blueprint('users_enhanced', __name__)

@users_enhanced_bp.route('/users', methods=['POST'])
@validate_json_data(user_schema)
@error_handler
def create_user():
    """Crear nuevo usuario"""
    data = request.validated_data
    
    # Obtener servicio del container
    user_repository = container.get(UserRepository)
    user_service = UserService(user_repository)
    
    # Crear usuario
    user = user_service.create_user(data)
    
    logger.info(f"User created: {user['username']}", extra={
        'user_id': user['id'],
        'role': user['role']
    })
    
    return created_response(
        data=user,
        message="Usuario creado exitosamente"
    )

@users_enhanced_bp.route('/users', methods=['GET'])
@error_handler
def get_users():
    """Obtener lista de usuarios con paginación"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '')
    role = request.args.get('role', '')
    
    # Obtener servicio del container
    user_repository = container.get(UserRepository)
    user_service = UserService(user_repository)
    
    # Obtener usuarios
    users, total = user_service.get_users_paginated(
        page=page, 
        per_page=per_page, 
        search=search, 
        role=role
    )
    
    return paginated_response(
        data=users,
        page=page,
        per_page=per_page,
        total=total,
        message="Usuarios obtenidos exitosamente"
    )

@users_enhanced_bp.route('/users/<int:user_id>', methods=['GET'])
@error_handler
def get_user(user_id):
    """Obtener usuario por ID"""
    # Obtener servicio del container
    user_repository = container.get(UserRepository)
    user_service = UserService(user_repository)
    
    # Obtener usuario
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        return not_found_response("Usuario")
    
    return success_response(
        data=user,
        message="Usuario obtenido exitosamente"
    )

@users_enhanced_bp.route('/users/<int:user_id>', methods=['PUT'])
@validate_json_data(user_schema)
@error_handler
def update_user(user_id):
    """Actualizar usuario"""
    data = request.validated_data
    
    # Obtener servicio del container
    user_repository = container.get(UserRepository)
    user_service = UserService(user_repository)
    
    # Actualizar usuario
    user = user_service.update_user(user_id, data)
    
    if not user:
        return not_found_response("Usuario")
    
    logger.info(f"User updated: {user['username']}", extra={
        'user_id': user['id'],
        'role': user['role']
    })
    
    return updated_response(
        data=user,
        message="Usuario actualizado exitosamente"
    )

@users_enhanced_bp.route('/users/<int:user_id>', methods=['DELETE'])
@error_handler
def delete_user(user_id):
    """Eliminar usuario"""
    # Obtener servicio del container
    user_repository = container.get(UserRepository)
    user_service = UserService(user_repository)
    
    # Eliminar usuario
    success = user_service.delete_user(user_id)
    
    if not success:
        return not_found_response("Usuario")
    
    logger.info(f"User deleted", extra={
        'user_id': user_id
    })
    
    return success_response(
        data=None,
        message="Usuario eliminado exitosamente"
    )

@users_enhanced_bp.route('/auth/login', methods=['POST'])
@validate_json_data(login_schema)
@error_handler
def login():
    """Autenticación de usuario"""
    data = request.validated_data
    
    # Obtener servicio del container
    user_repository = container.get(UserRepository)
    user_service = UserService(user_repository)
    
    # Autenticar usuario
    result = user_service.authenticate_user(
        data['username'], 
        data['password']
    )
    
    if not result:
        return unauthorized_response("Credenciales inválidas")
    
    # Generar tokens JWT
    from app.security.jwt_utils import create_access_token, create_refresh_token
    access_token = create_access_token(result['username'], result['role'], {'user_id': result['id']})
    refresh_token = create_refresh_token(result['username'])
    
    logger.info(f"User logged in: {data['username']}", extra={
        'user_id': result['id'],
        'role': result['role']
    })
    
    return success_response(
        data={
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'user': result
        },
        message="Login exitoso"
    )
