"""
Role Model - Sistema IAM Sabrositas POS
======================================
Modelo de roles con jerarquía y permisos granulares
"""

from datetime import datetime
from app import db
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import enum

class RoleType(enum.Enum):
    """Tipos de roles del sistema"""
    # Roles ODATA (Tecnología)
    SUPER_ADMIN = "super_admin"
    TECH_ADMIN = "tech_admin"
    TECH_SUPPORT = "tech_support"
    
    # Roles Cliente (Sabrositas)
    BUSINESS_OWNER = "business_owner"
    GLOBAL_ADMIN = "global_admin"
    STORE_ADMIN = "store_admin"
    SUPERVISOR = "supervisor"
    CASHIER = "cashier"
    WAITER = "waiter"
    KITCHEN = "kitchen"
    PURCHASING = "purchasing"

class PermissionCategory(enum.Enum):
    """Categorías de permisos"""
    SYSTEM = "system"           # Configuración del sistema
    USERS = "users"             # Gestión de usuarios
    PRODUCTS = "products"       # Gestión de productos
    INVENTORY = "inventory"     # Gestión de inventario
    SALES = "sales"             # Gestión de ventas
    PURCHASES = "purchases"     # Gestión de compras
    REPORTS = "reports"         # Reportes y analítica
    STORES = "stores"           # Gestión de tiendas
    KITCHEN = "kitchen"         # Operaciones de cocina
    PAYMENTS = "payments"       # Gestión de pagos
    AUDITING = "auditing"       # Auditoría y logs

# Tabla de asociación muchos-a-muchos entre roles y permisos
role_permissions = Table(
    'role_permissions',
    db.Model.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

# Tabla de asociación muchos-a-muchos entre usuarios y roles
user_roles = Table(
    'user_roles',
    db.Model.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('assigned_at', DateTime, default=datetime.utcnow),
    Column('assigned_by', Integer, ForeignKey('users.id'), nullable=True),
    Column('store_id', Integer, nullable=True),  # Rol específico para una tienda
    Column('is_active', Boolean, default=True)
)

@dataclass
class Role(db.Model):
    """Modelo de rol con jerarquía y permisos"""
    
    __tablename__ = 'roles'
    
    # Campos principales
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(100), unique=True, nullable=False, index=True)
    display_name: str = Column(String(150), nullable=False)
    description: str = Column(Text, nullable=True)
    
    # Tipo y categoría
    role_type: RoleType = Column(db.Enum(RoleType), nullable=False, index=True)
    organization: str = Column(String(50), nullable=False, index=True)  # 'odata' o 'sabrositas'
    
    # Jerarquía y configuración
    level: int = Column(Integer, default=1, index=True)  # Nivel jerárquico (1=más alto)
    is_system_role: bool = Column(Boolean, default=False)  # Rol del sistema (no editable)
    is_active: bool = Column(Boolean, default=True, index=True)
    
    # Restricciones
    max_users: int = Column(Integer, nullable=True)  # Máximo de usuarios con este rol
    requires_approval: bool = Column(Boolean, default=False)  # Requiere aprobación para asignar
    
    # Configuración por tienda
    is_store_specific: bool = Column(Boolean, default=False)  # Si el rol es específico por tienda
    can_access_all_stores: bool = Column(Boolean, default=False)  # Si puede acceder a todas las tiendas
    
    # Timestamps
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by: int = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relaciones
    permissions = relationship("Permission", secondary=role_permissions, back_populates="roles")
    users = relationship("User", secondary=user_roles, back_populates="roles_relationship", 
                        primaryjoin="Role.id == user_roles.c.role_id",
                        secondaryjoin="user_roles.c.user_id == User.id")
    creator = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<Role {self.name}: {self.display_name}>'
    
    @property
    def permission_names(self) -> List[str]:
        """Obtener nombres de permisos del rol"""
        return [perm.name for perm in self.permissions if perm.is_active]
    
    @property
    def user_count(self) -> int:
        """Contar usuarios activos con este rol"""
        return len([user for user in self.users if user.is_active])
    
    @property
    def is_odata_role(self) -> bool:
        """Verificar si es un rol de Odata"""
        return self.organization == 'odata'
    
    @property
    def is_client_role(self) -> bool:
        """Verificar si es un rol del cliente"""
        return self.organization == 'sabrositas'
    
    def has_permission(self, permission_name: str) -> bool:
        """Verificar si el rol tiene un permiso específico"""
        return permission_name in self.permission_names
    
    def can_assign_role(self, target_role: 'Role') -> bool:
        """Verificar si este rol puede asignar otro rol"""
        # Los roles de mayor nivel pueden asignar roles de menor nivel
        return self.level <= target_role.level and self.is_active
    
    def to_dict(self, include_permissions: bool = False) -> Dict[str, Any]:
        """Convertir a diccionario para API responses"""
        data = {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'role_type': self.role_type.value,
            'organization': self.organization,
            'level': self.level,
            'is_system_role': self.is_system_role,
            'is_active': self.is_active,
            'max_users': self.max_users,
            'requires_approval': self.requires_approval,
            'is_store_specific': self.is_store_specific,
            'can_access_all_stores': self.can_access_all_stores,
            'user_count': self.user_count,
            'is_odata_role': self.is_odata_role,
            'is_client_role': self.is_client_role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        
        if include_permissions:
            data['permissions'] = [perm.to_dict() for perm in self.permissions if perm.is_active]
            data['permission_names'] = self.permission_names
        
        return data

@dataclass
class Permission(db.Model):
    """Modelo de permiso granular"""
    
    __tablename__ = 'permissions'
    
    # Campos principales
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(100), unique=True, nullable=False, index=True)
    display_name: str = Column(String(150), nullable=False)
    description: str = Column(Text, nullable=True)
    
    # Categorización
    category: PermissionCategory = Column(db.Enum(PermissionCategory), nullable=False, index=True)
    resource: str = Column(String(50), nullable=False, index=True)  # Recurso afectado
    action: str = Column(String(50), nullable=False, index=True)    # Acción permitida
    
    # Configuración
    is_active: bool = Column(Boolean, default=True, index=True)
    is_system_permission: bool = Column(Boolean, default=False)  # Permiso del sistema (no editable)
    requires_context: bool = Column(Boolean, default=False)  # Requiere contexto adicional (ej. store_id)
    
    # Restricciones
    conditions: str = Column(Text, nullable=True)  # Condiciones adicionales en JSON
    
    # Timestamps
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    roles = relationship("Role", secondary=role_permissions, back_populates="permissions")
    
    def __repr__(self):
        return f'<Permission {self.name}: {self.action} {self.resource}>'
    
    @property
    def full_permission_name(self) -> str:
        """Nombre completo del permiso"""
        return f"{self.category.value}:{self.resource}:{self.action}"
    
    @property
    def role_count(self) -> int:
        """Contar roles que tienen este permiso"""
        return len([role for role in self.roles if role.is_active])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'category': self.category.value,
            'resource': self.resource,
            'action': self.action,
            'full_permission_name': self.full_permission_name,
            'is_active': self.is_active,
            'is_system_permission': self.is_system_permission,
            'requires_context': self.requires_context,
            'conditions': self.conditions,
            'role_count': self.role_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

@dataclass
class UserRole(db.Model):
    """Modelo de asignación de rol a usuario"""
    
    __tablename__ = 'user_role_assignments'
    
    # Campos principales
    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    role_id: int = Column(Integer, ForeignKey('roles.id'), nullable=False, index=True)
    
    # Contexto y restricciones
    store_id: int = Column(Integer, nullable=True, index=True)  # Rol específico para una tienda
    is_primary: bool = Column(Boolean, default=False)  # Rol principal del usuario
    is_active: bool = Column(Boolean, default=True, index=True)
    
    # Fechas de vigencia
    valid_from: datetime = Column(DateTime, default=datetime.utcnow)
    valid_until: datetime = Column(DateTime, nullable=True)
    
    # Auditoría
    assigned_at: datetime = Column(DateTime, default=datetime.utcnow)
    assigned_by: int = Column(Integer, ForeignKey('users.id'), nullable=True)
    revoked_at: datetime = Column(DateTime, nullable=True)
    revoked_by: int = Column(Integer, ForeignKey('users.id'), nullable=True)
    revocation_reason: str = Column(Text, nullable=True)
    
    # Relaciones
    user = relationship("User", foreign_keys=[user_id])
    role = relationship("Role")
    assigner = relationship("User", foreign_keys=[assigned_by])
    revoker = relationship("User", foreign_keys=[revoked_by])
    
    def __repr__(self):
        return f'<UserRole User:{self.user_id} Role:{self.role_id} Store:{self.store_id}>'
    
    @property
    def is_valid(self) -> bool:
        """Verificar si la asignación de rol es válida"""
        now = datetime.utcnow()
        
        if not self.is_active:
            return False
        
        if self.valid_from > now:
            return False
        
        if self.valid_until and self.valid_until < now:
            return False
        
        return True
    
    @property
    def is_expired(self) -> bool:
        """Verificar si la asignación ha expirado"""
        if not self.valid_until:
            return False
        
        return datetime.utcnow() > self.valid_until
    
    def revoke(self, revoked_by_user_id: int, reason: str = None):
        """Revocar asignación de rol"""
        self.is_active = False
        self.revoked_at = datetime.utcnow()
        self.revoked_by = revoked_by_user_id
        self.revocation_reason = reason
    
    def to_dict(self) -> Dict[str, Any]:
        """Convertir a diccionario para API responses"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role_id': self.role_id,
            'role_name': self.role.name if self.role else None,
            'role_display_name': self.role.display_name if self.role else None,
            'store_id': self.store_id,
            'is_primary': self.is_primary,
            'is_active': self.is_active,
            'is_valid': self.is_valid,
            'is_expired': self.is_expired,
            'valid_from': self.valid_from.isoformat() if self.valid_from else None,
            'valid_until': self.valid_until.isoformat() if self.valid_until else None,
            'assigned_at': self.assigned_at.isoformat() if self.assigned_at else None,
            'revoked_at': self.revoked_at.isoformat() if self.revoked_at else None,
            'revocation_reason': self.revocation_reason
        }
