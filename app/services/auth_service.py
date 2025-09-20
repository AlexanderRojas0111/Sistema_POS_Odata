"""
Auth Service - Sistema POS Sabrositas
====================================
Servicio para autenticación y autorización.
"""

from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from typing import Optional, Dict, Any
import logging

from app.models.user import User
from app import db

logger = logging.getLogger(__name__)

def token_required(f):
    """Decorator para requerir token JWT"""
    @wraps(f)
    @jwt_required()
    def decorated(*args, **kwargs):
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return jsonify({'error': 'Token inválido'}), 401
        
        # Verificar que el usuario existe y está activo
        user = User.query.get(current_user_id)
        if not user or not user.is_active:
            return jsonify({'error': 'Usuario no encontrado o inactivo'}), 401
        
        return f(*args, **kwargs)
    return decorated

def role_required(required_role: str):
    """Decorator para requerir rol específico"""
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated(*args, **kwargs):
            current_user_id = get_jwt_identity()
            if not current_user_id:
                return jsonify({'error': 'Token inválido'}), 401
            
            user = User.query.get(current_user_id)
            if not user or not user.is_active:
                return jsonify({'error': 'Usuario no encontrado o inactivo'}), 401
            
            if not user.is_authorized(required_role):
                return jsonify({'error': 'Permisos insuficientes'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator

def get_current_user() -> Optional[User]:
    """Obtener usuario actual desde el token JWT"""
    try:
        current_user_id = get_jwt_identity()
        if not current_user_id:
            return None
        
        return User.query.get(current_user_id)
    except Exception as e:
        logger.error(f"Error obteniendo usuario actual: {str(e)}")
        return None

def verify_user_permissions(user: User, required_permission: str) -> bool:
    """Verificar permisos específicos del usuario"""
    if not user or not user.is_active:
        return False
    
    # Mapeo de permisos a roles
    permission_roles = {
        'read_products': ['cashier', 'supervisor', 'manager', 'admin'],
        'write_products': ['supervisor', 'manager', 'admin'],
        'delete_products': ['manager', 'admin'],
        'read_users': ['supervisor', 'manager', 'admin'],
        'write_users': ['manager', 'admin'],
        'delete_users': ['admin'],
        'read_sales': ['cashier', 'supervisor', 'manager', 'admin'],
        'write_sales': ['cashier', 'supervisor', 'manager', 'admin'],
        'read_inventory': ['supervisor', 'manager', 'admin'],
        'write_inventory': ['supervisor', 'manager', 'admin'],
        'read_payroll': ['manager', 'admin'],
        'write_payroll': ['manager', 'admin'],
        'admin_access': ['admin']
    }
    
    required_roles = permission_roles.get(required_permission, [])
    return user.role in required_roles

def log_user_activity(user: User, action: str, details: Dict[str, Any] = None):
    """Registrar actividad del usuario"""
    try:
        logger.info(f"User {user.username} ({user.role}) performed action: {action}")
        if details:
            logger.info(f"Action details: {details}")
    except Exception as e:
        logger.error(f"Error logging user activity: {str(e)}")

class AuthService:
    """Servicio de autenticación"""
    
    def __init__(self):
        self.logger = logger
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Autenticar usuario con credenciales"""
        try:
            user = User.query.filter_by(username=username).first()
            
            if not user:
                self.logger.warning(f"Login attempt with non-existent username: {username}")
                return None
            
            if not user.is_active:
                self.logger.warning(f"Login attempt with inactive user: {username}")
                return None
            
            if not user.check_password(password):
                self.logger.warning(f"Failed login attempt for user: {username}")
                return None
            
            # Actualizar último login
            user.update_last_login()
            
            self.logger.info(f"Successful login for user: {username}")
            return user
            
        except Exception as e:
            self.logger.error(f"Error authenticating user {username}: {str(e)}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Obtener usuario por ID"""
        try:
            return User.query.get(user_id)
        except Exception as e:
            self.logger.error(f"Error getting user by ID {user_id}: {str(e)}")
            return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Obtener usuario por nombre de usuario"""
        try:
            return User.query.filter_by(username=username).first()
        except Exception as e:
            self.logger.error(f"Error getting user by username {username}: {str(e)}")
            return None
    
    def is_user_authorized(self, user: User, required_role: str) -> bool:
        """Verificar si el usuario está autorizado para un rol"""
        if not user or not user.is_active:
            return False
        
        return user.is_authorized(required_role)
    
    def get_user_permissions(self, user: User) -> list:
        """Obtener lista de permisos del usuario"""
        if not user or not user.is_active:
            return []
        
        # Mapeo de roles a permisos
        role_permissions = {
            'cashier': [
                'read_products', 'write_sales', 'read_sales'
            ],
            'supervisor': [
                'read_products', 'write_products', 'read_users',
                'read_sales', 'write_sales', 'read_inventory', 'write_inventory'
            ],
            'manager': [
                'read_products', 'write_products', 'delete_products',
                'read_users', 'write_users', 'read_sales', 'write_sales',
                'read_inventory', 'write_inventory', 'read_payroll', 'write_payroll'
            ],
            'admin': [
                'read_products', 'write_products', 'delete_products',
                'read_users', 'write_users', 'delete_users',
                'read_sales', 'write_sales', 'read_inventory', 'write_inventory',
                'read_payroll', 'write_payroll', 'admin_access'
            ]
        }
        
        return role_permissions.get(user.role, [])
