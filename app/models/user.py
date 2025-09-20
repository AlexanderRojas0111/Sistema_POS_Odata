"""
User Model - Sistema POS O'Data
==============================
Modelo de usuario con validaciones enterprise.
"""

from app import db
from datetime import datetime
from typing import Optional, Dict, Any
import bcrypt

class User(db.Model):
    """Modelo de usuario con validaciones enterprise"""
    
    __tablename__ = 'users'
    
    # Campos principales
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    
    # Estado y roles
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default='cashier', index=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Campos multi-sede (preparados para migración MySQL)
    assigned_store_id = db.Column(db.Integer, nullable=True, index=True)  # FK se agregará en migración MySQL
    can_access_all_stores = db.Column(db.Boolean, default=False)  # Para admins corporativos
    
    # Relaciones
    sales = db.relationship('Sale', backref='user', lazy=True, cascade='all, delete-orphan')
    # Relaciones IAM
    role_assignments = db.relationship('UserRole', foreign_keys='UserRole.user_id', lazy='dynamic')
    roles_relationship = db.relationship('Role', secondary='user_roles', back_populates='users',
                           primaryjoin='User.id == user_roles.c.user_id',
                           secondaryjoin='user_roles.c.role_id == Role.id')
    
    @property
    def roles(self):
        """Obtener roles activos del usuario"""
        from app.models.role import UserRole, Role
        return db.session.query(Role).join(UserRole).filter(
            UserRole.user_id == self.id,
            UserRole.is_active == True,
            Role.is_active == True
        ).all()
    
    @property
    def primary_role(self):
        """Obtener rol primario del usuario"""
        from app.models.role import UserRole, Role
        return db.session.query(Role).join(UserRole).filter(
            UserRole.user_id == self.id,
            UserRole.is_primary == True,
            UserRole.is_active == True,
            Role.is_active == True
        ).first()
    
    def has_role(self, role_name: str, store_id: int = None) -> bool:
        """Verificar si el usuario tiene un rol específico"""
        user_roles = self.roles
        for role in user_roles:
            if role.name == role_name:
                if store_id and role.is_store_specific:
                    # Verificar asignación específica de tienda
                    from app.models.role import UserRole
                    assignment = UserRole.query.filter_by(
                        user_id=self.id,
                        role_id=role.id,
                        store_id=store_id,
                        is_active=True
                    ).first()
                    return assignment is not None
                return True
        return False
    
    def __init__(self, username: str, email: str, password: str, **kwargs):
        """Constructor con validaciones"""
        self.username = username
        self.email = email
        self.set_password(password)
        
        # Asignar otros campos
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def set_password(self, password: str) -> None:
        """Establecer contraseña con hash seguro"""
        if not password or len(password) < 6:
            raise ValueError("Password must be at least 6 characters long")
        
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Verificar contraseña"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )
    
    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convertir a diccionario para serialización"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'role': self.role,
            'assigned_store_id': self.assigned_store_id,
            'assigned_store_name': None,  # Se implementará con migración MySQL
            'can_access_all_stores': self.can_access_all_stores,
            'managed_stores_count': 0,  # Se implementará con migración MySQL
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
        
        return data
    
    def update_last_login(self) -> None:
        """Actualizar último login"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def is_authorized(self, required_role: str) -> bool:
        """Verificar autorización por rol"""
        role_hierarchy = {
            'cashier': 1,
            'supervisor': 2,
            'manager': 3,
            'admin': 4
        }
        
        user_level = role_hierarchy.get(self.role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    def __repr__(self) -> str:
        return f'<User {self.username}>'
