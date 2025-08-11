from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token, create_refresh_token
from app.crud.users import users_crud
from app.schemas import UserCreate, UserUpdate, UserResponse, UserLogin
from app.core.database import db
from werkzeug.security import check_password_hash

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/login', methods=['POST'])
def login():
    """Autenticación de usuario"""
    try:
        data = request.get_json()
        login_data = UserLogin(**data)
        
        user = users_crud.get_by_email(login_data.email)
        if not user or not check_password_hash(user.password_hash, login_data.password):
            return jsonify({'error': 'Credenciales inválidas'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Usuario inactivo'}), 401
        
        access_token = create_access_token(identity=user.id)
        refresh_token = create_refresh_token(identity=user.id)
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': UserResponse.from_orm(user).dict()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    """Renovar token de acceso"""
    try:
        current_user_id = get_jwt_identity()
        access_token = create_access_token(identity=current_user_id)
        return jsonify({'access_token': access_token}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    """Obtener todos los usuarios"""
    try:
        users = users_crud.get_all()
        return jsonify([UserResponse.from_orm(user).dict() for user in users]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user(user_id):
    """Obtener un usuario específico"""
    try:
        user = users_crud.get(user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        return jsonify(UserResponse.from_orm(user).dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    """Crear un nuevo usuario"""
    try:
        data = request.get_json()
        user_data = UserCreate(**data)
        user = users_crud.create(user_data)
        db.session.commit()
        return jsonify(UserResponse.from_orm(user).dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Actualizar un usuario"""
    try:
        data = request.get_json()
        user_data = UserUpdate(**data)
        user = users_crud.update(user_id, user_data)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        db.session.commit()
        return jsonify(UserResponse.from_orm(user).dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@bp.route('/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Eliminar un usuario"""
    try:
        success = users_crud.delete(user_id)
        if not success:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        db.session.commit()
        return jsonify({'message': 'Usuario eliminado correctamente'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Obtener perfil del usuario actual"""
    try:
        current_user_id = get_jwt_identity()
        user = users_crud.get(current_user_id)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        return jsonify(UserResponse.from_orm(user).dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Actualizar perfil del usuario actual"""
    try:
        current_user_id = get_jwt_identity()
        data = request.get_json()
        user_data = UserUpdate(**data)
        user = users_crud.update(current_user_id, user_data)
        if not user:
            return jsonify({'error': 'Usuario no encontrado'}), 404
        db.session.commit()
        return jsonify(UserResponse.from_orm(user).dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400 