from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from app.models.user import User, UserRole
from app.core.database import db
from app.core.security import SecurityManager
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

bp = Blueprint('users', __name__, url_prefix='/usuarios')

security_manager = SecurityManager()

@bp.route('/login', methods=['POST'])
def login():
    """
    Autenticación de usuario
    ---
    tags:
      - Usuarios
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
      401:
        description: Credenciales inválidas
    """
    try:
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

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """
    Renovar token de acceso
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    responses:
      200:
        description: Token renovado
        schema:
          type: object
          properties:
            access_token:
              type: string
      401:
        description: Token inválido
    """
    try:
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(
            identity=current_user_id,
            expires_delta=timedelta(hours=1)
        )
        
        return jsonify({'access_token': new_access_token}), 200
        
    except Exception as e:
        logger.error(f"Error renovando token: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """
    Obtener todos los usuarios
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    parameters:
      - name: page
        in: query
        type: integer
        description: Número de página
      - name: per_page
        in: query
        type: integer
        description: Elementos por página
      - name: role
        in: query
        type: string
        description: Filtrar por rol
    responses:
      200:
        description: Lista de usuarios
        schema:
          type: object
          properties:
            users:
              type: array
              items:
                $ref: '#/definitions/User'
            total:
              type: integer
            pages:
              type: integer
            current_page:
              type: integer
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Solo administradores pueden ver todos los usuarios
        if current_user.role != UserRole.ADMIN:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        role_filter = request.args.get('role')
        
        query = User.query
        
        if role_filter:
            try:
                role_enum = UserRole(role_filter.upper())
                query = query.filter(User.role == role_enum)
            except ValueError:
                return jsonify({'error': 'Rol inválido'}), 400
        
        users = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'users': [
                {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role.value,
                    'is_active': user.is_active,
                    'created_at': user.created_at.isoformat() if user.created_at else None
                }
                for user in users.items
            ],
            'total': users.total,
            'pages': users.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo usuarios: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """
    Obtener un usuario específico
    ---
    tags:
      - Usuarios
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID del usuario
    security:
      - Bearer: []
    responses:
      200:
        description: Usuario encontrado
        schema:
          $ref: '#/definitions/User'
      404:
        description: Usuario no encontrado
      403:
        description: Acceso denegado
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Usuarios solo pueden ver su propio perfil, admins pueden ver todos
        if current_user.id != user_id and current_user.role != UserRole.ADMIN:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        user = User.query.get_or_404(user_id)
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo usuario {user_id}: {e}")
        return jsonify({'error': 'Usuario no encontrado'}), 404

@bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    """
    Crear un nuevo usuario
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
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
            - role
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
              description: Rol del usuario (ADMIN, MANAGER, EMPLOYEE)
    responses:
      201:
        description: Usuario creado exitosamente
      400:
        description: Datos inválidos
      403:
        description: Acceso denegado
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Solo administradores pueden crear usuarios
        if current_user.role != UserRole.ADMIN:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Username, email y password son requeridos'}), 400
        
        # Validar rol
        try:
            role = UserRole(data['role'].upper())
        except ValueError:
            return jsonify({'error': 'Rol inválido. Use: ADMIN, MANAGER, EMPLOYEE'}), 400
        
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username ya existe'}), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email ya existe'}), 409
        
        # Crear usuario
        user = User(
            username=data['username'],
            email=data['email'],
            role=role
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"Usuario creado: {user.username} con rol {user.role.value}")
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value,
            'is_active': user.is_active
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creando usuario: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """
    Actualizar un usuario
    ---
    tags:
      - Usuarios
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID del usuario
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            username:
              type: string
            email:
              type: string
            role:
              type: string
            is_active:
              type: boolean
    responses:
      200:
        description: Usuario actualizado
      404:
        description: Usuario no encontrado
      403:
        description: Acceso denegado
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Solo administradores pueden actualizar usuarios
        if current_user.role != UserRole.ADMIN:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if data.get('username'):
            # Verificar que el username no esté en uso
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': 'Username ya existe'}), 409
            user.username = data['username']
        
        if data.get('email'):
            # Verificar que el email no esté en uso
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'error': 'Email ya existe'}), 409
            user.email = data['email']
        
        if data.get('role'):
            try:
                role = UserRole(data['role'].upper())
                user.role = role
            except ValueError:
                return jsonify({'error': 'Rol inválido'}), 400
        
        if data.get('is_active') is not None:
            user.is_active = bool(data['is_active'])
        
        db.session.commit()
        
        logger.info(f"Usuario actualizado: {user.username}")
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value,
            'is_active': user.is_active
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando usuario {user_id}: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """
    Eliminar un usuario
    ---
    tags:
      - Usuarios
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
        description: ID del usuario
    security:
      - Bearer: []
    responses:
      200:
        description: Usuario eliminado
      404:
        description: Usuario no encontrado
      403:
        description: Acceso denegado
    """
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        # Solo administradores pueden eliminar usuarios
        if current_user.role != UserRole.ADMIN:
            return jsonify({'error': 'Acceso denegado'}), 403
        
        # No permitir eliminar el propio usuario
        if current_user.id == user_id:
            return jsonify({'error': 'No puedes eliminar tu propio usuario'}), 400
        
        user = User.query.get_or_404(user_id)
        username = user.username
        
        db.session.delete(user)
        db.session.commit()
        
        logger.info(f"Usuario eliminado: {username}")
        return jsonify({'message': f'Usuario {username} eliminado exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error eliminando usuario {user_id}: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Obtener perfil del usuario autenticado
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    responses:
      200:
        description: Perfil del usuario
        schema:
          $ref: '#/definitions/User'
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        return jsonify({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role.value,
            'is_active': user.is_active,
            'created_at': user.created_at.isoformat() if user.created_at else None,
            'updated_at': user.updated_at.isoformat() if user.updated_at else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error obteniendo perfil: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """
    Cambiar contraseña del usuario autenticado
    ---
    tags:
      - Usuarios
    security:
      - Bearer: []
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - current_password
            - new_password
          properties:
            current_password:
              type: string
              description: Contraseña actual
            new_password:
              type: string
              description: Nueva contraseña
    responses:
      200:
        description: Contraseña cambiada exitosamente
      400:
        description: Contraseña actual incorrecta
    """
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        data = request.get_json()
        
        if not data or not data.get('current_password') or not data.get('new_password'):
            return jsonify({'error': 'Contraseña actual y nueva son requeridas'}), 400
        
        if not user.check_password(data['current_password']):
            return jsonify({'error': 'Contraseña actual incorrecta'}), 400
        
        user.set_password(data['new_password'])
        db.session.commit()
        
        logger.info(f"Contraseña cambiada para usuario: {user.username}")
        return jsonify({'message': 'Contraseña cambiada exitosamente'}), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error cambiando contraseña: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500 