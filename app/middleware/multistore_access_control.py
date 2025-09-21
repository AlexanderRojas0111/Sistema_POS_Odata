"""
Middleware de Control de Acceso Multi-Tienda
============================================
Sistema POS Sabrositas v2.0.0 - Enterprise Multi-Store Access Control
"""

from functools import wraps
from typing import List, Optional, Dict, Any
from flask import request, jsonify, g, current_app
from app.models.user import User
from app.models.store import Store
from app.models.role import Role, UserRole
from app.services.iam_service import IAMService
from app.exceptions import AuthenticationError, AuthorizationError, ValidationError
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class MultiStoreAccessControl:
    """Middleware para control de acceso multi-tienda enterprise"""
    
    def __init__(self, app=None):
        self.iam_service = IAMService()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar middleware con la aplicación Flask"""
        app.multistore_access = self
        
        @app.before_request
        def load_multistore_context():
            """Cargar contexto multi-tienda en cada request"""
            self._load_store_context()
            self._validate_store_access()
            self._log_access_attempt()
    
    def _load_store_context(self):
        """Cargar contexto de tienda del request"""
        # Inicializar contexto
        g.current_store_id = None
        g.current_store = None
        g.accessible_stores = []
        g.store_permissions = []
        
        # Obtener store_id del header o parámetro
        store_id = (
            request.headers.get('X-Store-ID') or
            request.args.get('store_id') or
            request.json.get('store_id') if request.is_json else None
        )
        
        if store_id:
            try:
                store_id = int(store_id)
                store = Store.query.filter_by(id=store_id, is_active=True).first()
                
                if store:
                    g.current_store_id = store_id
                    g.current_store = store
                    logger.debug(f"Store context loaded: {store.code} - {store.name}")
                else:
                    logger.warning(f"Invalid store_id requested: {store_id}")
            except (ValueError, TypeError):
                logger.warning(f"Invalid store_id format: {store_id}")
        
        # Cargar tiendas accesibles para el usuario actual
        if g.get('current_user_id'):
            g.accessible_stores = self._get_user_accessible_stores(g.current_user_id)
            g.store_permissions = self._get_user_store_permissions(
                g.current_user_id, 
                g.current_store_id
            )
    
    def _validate_store_access(self):
        """Validar que el usuario tenga acceso a la tienda solicitada"""
        # Skip validation for public endpoints
        if self._is_public_endpoint():
            return
        
        # Skip if no authentication required
        if not g.get('current_user_id'):
            return
        
        # Skip if no specific store requested
        if not g.current_store_id:
            return
        
        # Verificar acceso a la tienda
        if not self._user_can_access_store(g.current_user_id, g.current_store_id):
            raise AuthorizationError(
                f"Usuario no tiene acceso a la tienda {g.current_store_id}"
            )
    
    def _log_access_attempt(self):
        """Registrar intento de acceso para auditoría"""
        if g.get('current_user_id') and g.get('current_store_id'):
            # Log de acceso exitoso
            logger.info(
                f"Store access: user_id={g.current_user_id}, "
                f"store_id={g.current_store_id}, "
                f"endpoint={request.endpoint}, "
                f"method={request.method}"
            )
    
    def _is_public_endpoint(self) -> bool:
        """Verificar si el endpoint es público"""
        public_endpoints = {
            'health', 'login', 'register', 'static', 
            'favicon.ico', 'robots.txt'
        }
        
        return (
            request.endpoint in public_endpoints or
            request.path.startswith('/static/') or
            request.path.startswith('/api/v1/health') or
            request.path.startswith('/api/v1/auth/login')
        )
    
    def _get_user_accessible_stores(self, user_id: int) -> List[Store]:
        """Obtener tiendas accesibles para un usuario"""
        try:
            user_roles = self.iam_service.get_user_roles(user_id)
            accessible_stores = []
            
            for role in user_roles:
                if role.can_access_all_stores:
                    # Usuario con acceso global - todas las tiendas activas
                    return Store.query.filter_by(is_active=True).all()
                elif role.is_store_specific:
                    # Usuario con acceso específico - solo sus tiendas asignadas
                    user_role_assignments = UserRole.query.filter_by(
                        user_id=user_id,
                        role_id=role.id,
                        is_active=True
                    ).all()
                    
                    for assignment in user_role_assignments:
                        if assignment.store_id:
                            store = Store.query.filter_by(
                                id=assignment.store_id,
                                is_active=True
                            ).first()
                            if store and store not in accessible_stores:
                                accessible_stores.append(store)
            
            return accessible_stores
            
        except Exception as e:
            logger.error(f"Error getting accessible stores for user {user_id}: {e}")
            return []
    
    def _get_user_store_permissions(self, user_id: int, store_id: int = None) -> List[str]:
        """Obtener permisos específicos del usuario en una tienda"""
        try:
            return self.iam_service.get_user_permissions(user_id, store_id)
        except Exception as e:
            logger.error(f"Error getting store permissions: {e}")
            return []
    
    def _user_can_access_store(self, user_id: int, store_id: int) -> bool:
        """Verificar si un usuario puede acceder a una tienda específica"""
        accessible_stores = g.get('accessible_stores', [])
        return any(store.id == store_id for store in accessible_stores)

# Decoradores para control de acceso por tienda

def require_store_access(allow_global: bool = True):
    """Decorator para requerir acceso a tienda específica"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.get('current_user_id'):
                raise AuthenticationError("Autenticación requerida")
            
            # Si no se especifica tienda y se permite acceso global
            if not g.get('current_store_id') and allow_global:
                # Verificar que el usuario tenga roles globales
                user_roles = g.get('user_roles', [])
                has_global_role = any(role.can_access_all_stores for role in user_roles)
                
                if not has_global_role:
                    raise AuthorizationError("Se requiere especificar tienda o tener acceso global")
                
                return f(*args, **kwargs)
            
            # Verificar acceso a tienda específica
            if not g.get('current_store_id'):
                raise ValidationError("ID de tienda requerido")
            
            if not current_app.multistore_access._user_can_access_store(
                g.current_user_id, 
                g.current_store_id
            ):
                raise AuthorizationError(f"Sin acceso a tienda {g.current_store_id}")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_store_role(role_name: str, store_specific: bool = True):
    """Decorator para requerir rol específico en una tienda"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.get('current_user_id'):
                raise AuthenticationError("Autenticación requerida")
            
            user_roles = g.get('user_roles', [])
            
            # Buscar el rol requerido
            has_role = False
            for role in user_roles:
                if role.name == role_name:
                    if store_specific and role.is_store_specific:
                        # Verificar que el rol esté asignado para esta tienda
                        if g.get('current_store_id'):
                            assignment = UserRole.query.filter_by(
                                user_id=g.current_user_id,
                                role_id=role.id,
                                store_id=g.current_store_id,
                                is_active=True
                            ).first()
                            if assignment and assignment.is_valid:
                                has_role = True
                                break
                    elif not store_specific or role.can_access_all_stores:
                        has_role = True
                        break
            
            if not has_role:
                raise AuthorizationError(f"Rol requerido: {role_name}")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_store_permission(permission: str):
    """Decorator para requerir permiso específico en contexto de tienda"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.get('current_user_id'):
                raise AuthenticationError("Autenticación requerida")
            
            store_id = g.get('current_store_id')
            has_permission = current_app.multistore_access.iam_service.has_permission(
                g.current_user_id, 
                permission, 
                store_id
            )
            
            if not has_permission:
                raise AuthorizationError(f"Permiso requerido: {permission}")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_any_store_role(role_names: List[str]):
    """Decorator para requerir cualquiera de los roles especificados"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.get('current_user_id'):
                raise AuthenticationError("Autenticación requerida")
            
            user_roles = g.get('user_roles', [])
            user_role_names = [role.name for role in user_roles]
            
            has_required_role = any(role_name in user_role_names for role_name in role_names)
            
            if not has_required_role:
                raise AuthorizationError(f"Se requiere uno de estos roles: {', '.join(role_names)}")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def store_admin_required(f):
    """Decorator para requerir rol de administrador de tienda"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.get('current_user_id'):
            raise AuthenticationError("Autenticación requerida")
        
        # Verificar roles de administrador
        admin_roles = ['super_admin', 'global_admin', 'store_admin']
        user_roles = g.get('user_roles', [])
        
        has_admin_role = any(
            role.name in admin_roles for role in user_roles
        )
        
        if not has_admin_role:
            raise AuthorizationError("Se requiere rol de administrador")
        
        return f(*args, **kwargs)
    
    return decorated_function

def global_access_only(f):
    """Decorator para permitir solo usuarios con acceso global"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.get('current_user_id'):
            raise AuthenticationError("Autenticación requerida")
        
        user_roles = g.get('user_roles', [])
        has_global_access = any(role.can_access_all_stores for role in user_roles)
        
        if not has_global_access:
            raise AuthorizationError("Se requiere acceso global al sistema")
        
        return f(*args, **kwargs)
    
    return decorated_function

# Funciones de utilidad para contexto de tienda

def get_current_store() -> Optional[Store]:
    """Obtener tienda actual del contexto"""
    return g.get('current_store')

def get_current_store_id() -> Optional[int]:
    """Obtener ID de tienda actual del contexto"""
    return g.get('current_store_id')

def get_accessible_stores() -> List[Store]:
    """Obtener lista de tiendas accesibles para el usuario actual"""
    return g.get('accessible_stores', [])

def get_store_permissions() -> List[str]:
    """Obtener permisos del usuario en la tienda actual"""
    return g.get('store_permissions', [])

def can_access_store(store_id: int) -> bool:
    """Verificar si el usuario actual puede acceder a una tienda"""
    accessible_stores = get_accessible_stores()
    return any(store.id == store_id for store in accessible_stores)

def get_user_store_context() -> Dict[str, Any]:
    """Obtener contexto completo de tienda del usuario"""
    return {
        'current_store_id': get_current_store_id(),
        'current_store': get_current_store().to_dict() if get_current_store() else None,
        'accessible_stores': [store.to_dict() for store in get_accessible_stores()],
        'store_permissions': get_store_permissions(),
        'can_access_all_stores': any(
            role.can_access_all_stores 
            for role in g.get('user_roles', [])
        )
    }

def validate_store_operation(operation: str, store_id: int = None) -> bool:
    """Validar si el usuario puede realizar una operación en una tienda"""
    target_store_id = store_id or get_current_store_id()
    
    if not target_store_id:
        return False
    
    if not can_access_store(target_store_id):
        return False
    
    # Validar permisos específicos de la operación
    permission_map = {
        'read_sales': 'sales:store:read',
        'write_sales': 'sales:register:write',
        'read_inventory': 'inventory:store:read',
        'write_inventory': 'inventory:store:write',
        'read_reports': 'reports:store:read',
        'manage_users': 'users:store:write'
    }
    
    required_permission = permission_map.get(operation)
    if required_permission:
        return current_app.multistore_access.iam_service.has_permission(
            g.current_user_id,
            required_permission,
            target_store_id
        )
    
    return True

def log_store_activity(activity: str, details: Dict[str, Any] = None):
    """Registrar actividad específica de tienda para auditoría"""
    logger.info(
        f"Store activity: {activity}",
        extra={
            'user_id': g.get('current_user_id'),
            'store_id': get_current_store_id(),
            'store_code': get_current_store().code if get_current_store() else None,
            'activity': activity,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat(),
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        }
    )
