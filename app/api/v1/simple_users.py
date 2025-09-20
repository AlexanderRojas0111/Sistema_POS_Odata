"""
Simple Users API - Sistema POS O'Data
====================================
Versión simplificada de endpoints de usuarios para deployment.
"""

from flask import Blueprint, request, jsonify
from app import db
from app.models.user import User
from app.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

# Crear blueprint
simple_users_bp = Blueprint('simple_users', __name__)

@simple_users_bp.route('/simple/users', methods=['POST'])
def create_user():
    """Crear usuario - versión simplificada"""
    try:
        data = request.get_json()
        
        if not data:
            raise ValidationError("Request body is required")
        
        # Validar datos requeridos
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if not username or not email or not password:
            raise ValidationError("username, email, and password are required")
        
        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            raise ValidationError(f"Username '{username}' already exists", field="username")
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            raise ValidationError(f"Email '{email}' already exists", field="email")
        
        # Crear usuario
        user = User(
            username=username,
            email=email,
            password=password,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            role=data.get('role', 'cashier')
        )
        
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"User created: {username}")
        
        return jsonify({
            'status': 'success',
            'data': user.to_dict(),
            'message': 'User created successfully'
        }), 201
        
    except ValidationError as e:
        logger.warning(f"Validation error in create_user: {e.message}")
        return jsonify(e.to_dict()), e.status_code
    
    except Exception as e:
        logger.error(f"Unexpected error in create_user: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@simple_users_bp.route('/simple/users', methods=['GET'])
def get_users():
    """Obtener usuarios - versión simplificada"""
    try:
        users = User.query.all()
        return jsonify({
            'status': 'success',
            'data': [user.to_dict() for user in users]
        })
        
    except Exception as e:
        logger.error(f"Error in get_users: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500

@simple_users_bp.route('/simple/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Obtener usuario por ID - versión simplificada"""
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({
                'error': {
                    'code': 'NOT_FOUND',
                    'message': 'User not found'
                }
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': user.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error in get_user: {str(e)}")
        return jsonify({
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An internal error occurred'
            }
        }), 500
