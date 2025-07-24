from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
import enum
from app.models.base import BaseModel

class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"

class User(BaseModel):
    """Modelo para usuarios"""
    __tablename__ = 'users'

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.EMPLOYEE)
    is_active = Column(Boolean, default=True)
    
    # Relaciones
    sales = relationship('Sale', back_populates='user', lazy='dynamic')
    inventory_changes = relationship('Inventory', back_populates='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Establece el hash de la contraseña"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verifica la contraseña"""
        return check_password_hash(self.password_hash, password)

    def has_role(self, role):
        """Verifica si el usuario tiene un rol específico"""
        return self.role == role 