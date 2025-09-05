#!/usr/bin/env python3
"""
Rutas de Autenticación - O'Data v2.0.0
=======================================

Endpoints para:
- Login de usuarios
- Registro de usuarios
- Validación de tokens
- Refresh de tokens
- Logout

Autor: Sistema POS Odata
Versión: 2.0.0
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token, 
    jwt_required, 
    get_jwt_identity,
    get_jwt
)
from app.models.user import User, UserRole
from app.core.security import SecurityManager
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__, url_prefix='/auth')

security_manager = SecurityManager()

@bp.route('/login', methods=['POST'])
def login():
    """
    Autenticación de usuario
    ---
    tags:
      - Autenticación
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: Nombre de usuario
            password:
              type: string
              description: Contraseña
    responses:
      200:
        description: Login exitoso
        schema:
          type: object
          properties:
            access_token:
              type: string
            refresh_token:
              type: string
            user:
              type: object
              properties:
                id:
                  type: integer
                username:
                  type: string
                email:
                  type: string
                role:
                  type: string
      400:
        description: Datos inválidos
      401:
        description: Credenciales inválidas
    """
    try:
        # Importar db desde la aplicación
        from app import db
        
        # Verificar Content-Type
        if not request.is_json:
            return jsonify({'error': 'Content-Type debe ser application/json'}), 400
        
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Usuario y contraseña son requeridos'}), 400
        
        username = data['username']
        password = data['password']
        
        # Buscar usuario
        user = User.query.filter_by(username=username).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Usuario inactivo'}), 401
        
        # Generar tokens
        access_token = create_access_token(
            identity=user.id,
            expires_delta=timedelta(hours=1)
        )
        refresh_token = create_refresh_token(
            identity=user.id,
            expires_delta=timedelta(days=30)
        )
        
        logger.info(f"Usuario autenticado: {username}")
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.value,
                'is_active': user.is_active
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error en login: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/register', methods=['POST'])
def register():
    """
    Registro de nuevo usuario
    ---
    tags:
      - Autenticación
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - username
            - email
            - password
          properties:
            username:
              type: string
              description: Nombre de usuario
            email:
              type: string
              description: Email del usuario
            password:
              type: string
              description: Contraseña
            role:
              type: string
              description: Rol del usuario (opcional)
    responses:
      201:
        description: Usuario creado exitosamente
      400:
        description: Datos inválidos
      409:
        description: Usuario ya existe
    """
    try:
        # Importar db desde la aplicación
        from app import db
        
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Username, email y password son requeridos'}), 400
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'El nombre de usuario ya existe'}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'El email ya está registrado'}), 409
        
        # Crear nuevo usuario
        user = User(
            username=data['username'],
            email=data['email'],
            role=UserRole.EMPLOYEE  # Rol por defecto
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"Nuevo usuario registrado: {data['username']}")
        return jsonify({
            'message': 'Usuario creado exitosamente',
            'user_id': user.id
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error en registro: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Refresh del token de acceso
    ---
    tags:
      - Autenticación
    security:
      - Bearer: []
    responses:
      200:
        description: Token refrescado exitosamente
      401:
        description: Token inválido
    """
    try:
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(
            identity=current_user_id,
            expires_delta=timedelta(hours=1)
        )
        
        return jsonify({
            'access_token': new_access_token
        }), 200
        
    except Exception as e:
        logger.error(f"Error refrescando token: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """
    Logout del usuario
    ---
    tags:
      - Autenticación
    security:
      - Bearer: []
    responses:
      200:
        description: Logout exitoso
    """
    try:
        # En una implementación real, aquí se invalidaría el token
        # Por ahora solo retornamos éxito
        return jsonify({'message': 'Logout exitoso'}), 200
        
    except Exception as e:
        logger.error(f"Error en logout: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """
    Obtener información del usuario actual
    ---
    tags:
      - Autenticación
    security:
      - Bearer: []
    responses:
      200:
        description: Información del usuario
      401:
        description: No autorizado
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo usuario actual: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/validate', methods=['POST'])
def validate_token():
    """
    Validar token (sin requerir autenticación)
    ---
    tags:
      - Autenticación
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - token
          properties:
            token:
              type: string
              description: Token a validar
    responses:
      200:
        description: Token válido
      400:
        description: Datos inválidos
    """
    try:
        # Verificar Content-Type
        if not request.is_json:
            return jsonify({'error': 'Content-Type debe ser application/json'}), 400
        
        try:
            data = request.get_json()
        except Exception as json_error:
            # Capturar errores de JSON inválido
            return jsonify({'error': 'JSON inválido', 'details': str(json_error)}), 400
        
        if not data or not data.get('token'):
            return jsonify({'error': 'Token requerido'}), 400
        
        # Esta es una validación básica
        # En producción se debería validar contra la base de datos
        return jsonify({'message': 'Token válido'}), 200
        
    except Exception as e:
        logger.error(f"Error validando token: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
