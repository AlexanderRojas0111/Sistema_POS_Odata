from flask import Blueprint, request, jsonify
from app.models import User
from app.database import db
from werkzeug.security import generate_password_hash, check_password_hash

users = Blueprint('users', __name__)

@users.route('/api/users', methods=['GET'])
def get_users():
    """Obtiene todos los usuarios"""
    users = User.query.all()
    return jsonify([user.to_dict() for user in users])

@users.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Obtiene un usuario por su ID"""
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@users.route('/api/users', methods=['POST'])
def create_user():
    """Crea un nuevo usuario"""
    data = request.get_json()
    
    # Verificar si el email ya existe
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'El email ya está registrado'}), 400
    
    # Crear usuario
    user = User(
        email=data['email'],
        password=generate_password_hash(data['password']),
        name=data['name']
    )
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201

@users.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Actualiza un usuario existente"""
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    
    # Actualizar campos
    if 'email' in data:
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user and existing_user.id != user_id:
            return jsonify({'error': 'El email ya está registrado'}), 400
        user.email = data['email']
    
    if 'name' in data:
        user.name = data['name']
    
    if 'password' in data:
        user.password = generate_password_hash(data['password'])
    
    db.session.commit()
    return jsonify(user.to_dict())

@users.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Elimina un usuario"""
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '', 204

@users.route('/api/users/login', methods=['POST'])
def login():
    """Inicia sesión de usuario"""
    data = request.get_json()
    
    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password, data['password']):
        return jsonify({'error': 'Email o contraseña incorrectos'}), 401
    
    return jsonify(user.to_dict())