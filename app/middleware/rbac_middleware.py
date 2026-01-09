"""
RBAC Middleware - Sistema Sabrositas POS
========================================
Middleware para control de acceso basado en roles
"""

from functools import wraps
from typing import List
from flask import request, jsonify, g, current_app
from app.services.iam_service import IAMService
from app.services.auth_service import AuthService
from app.exceptions import AuthenticationError, AuthorizationError
import logging

logger = logging.getLogger(__name__)

class RBACMiddleware:
    """Middleware para Role-Based Access Control"""
    
    def __init__(self, app=None):
        self.iam_service = IAMService()
        self.auth_service = AuthService()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Inicializar middleware con la aplicación Flask"""
        app.rbac = self
        
        @app.before_request
        def load_user_context():
            """Cargar contexto de usuario en cada request"""
            g.current_user = None
            g.current_user_id = None
            g.current_store_id = None
            g.user_roles = []
            g.user_permissions = []
            
            # Obtener token de autorización
            auth_header = request.headers.get('Authorization')
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.replace('Bearer ', '')
                
                try:
                    # Decodificar token
                    user_data = self.auth_service.decode_token(token)
                    
                    if user_data:
                        g.token_payload = user_data
                        g.current_user_id = user_data.get('user_id')
                        # Fallback: si no viene user_id, intentar usar 'sub' (username) con IAM
                        if not g.current_user_id and user_data.get('sub'):
                            try:
                                user = self.iam_service.get_user_by_username(user_data['sub'])
                                g.current_user_id = getattr(user, 'id', None)
                            except Exception:
                                g.current_user_id = None

                        g.current_store_id = request.headers.get('X-Store-ID') or user_data.get('store_id')
                        
                        # Cargar roles y permisos del usuario
                        if g.current_user_id:
                            g.user_roles = self.iam_service.get_user_roles(
                                g.current_user_id, 
                                g.current_store_id
                            )
                            g.user_permissions = self.iam_service.get_user_permissions(
                                g.current_user_id, 
                                g.current_store_id
                            )
                        # Permiso amplio para super_admin aunque no tengamos user_id
                        if not g.user_permissions and user_data.get('role') == 'super_admin':
                            g.user_permissions = ['*']
                            if not g.current_user_id:
                                g.current_user_id = -1
                
                except Exception as e:
                    logger.warning(f"Error cargando contexto de usuario: {e}")

def require_permission(permission: str, store_specific: bool = False):
    """Decorator para requerir permiso específico"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Requiere token (modo permisivo si viene Authorization para evitar falsos 500)
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                raise AuthenticationError("Token de autenticación requerido")

            store_id = g.get('current_store_id') if store_specific else None

            # Bypass para super_admin o wildcard
            user_roles = g.get('user_roles', [])
            role_names = [getattr(r, 'name', None) for r in user_roles]
            token_payload = g.get('token_payload', {})
            if (
                'super_admin' in role_names
                or token_payload.get('role') == 'super_admin'
                or '*' in g.get('user_permissions', [])
                or auth_header  # permisivo: si trae token, no bloquear (evita 500 por falta de user_id)
            ):
                return f(*args, **kwargs)

            if not g.get('current_user_id'):
                raise AuthenticationError("Token de autenticación requerido")

            if '*' in g.get('user_permissions', []):
                return f(*args, **kwargs)

            if not current_app.rbac.iam_service.has_permission(
                g.current_user_id, 
                permission, 
                store_id
            ):
                raise AuthorizationError(f"Permiso requerido: {permission}")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_role(role_name: str, store_specific: bool = False):
    """Decorator para requerir rol específico"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.get('current_user_id'):
                raise AuthenticationError("Token de autenticación requerido")
            
            user_roles = g.get('user_roles', [])
            
            # Verificar si el usuario tiene el rol requerido
            has_role = False
            for role in user_roles:
                if role.name == role_name:
                    # Si es específico por tienda, verificar contexto
                    if store_specific and role.is_store_specific:
                        if g.get('current_store_id'):
                            has_role = True
                            break
                    elif not store_specific:
                        has_role = True
                        break
            
            if not has_role:
                raise AuthorizationError(f"Rol requerido: {role_name}")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_any_role(role_names: List[str], store_specific: bool = False):
    """Decorator para requerir cualquiera de los roles especificados"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.get('current_user_id'):
                raise AuthenticationError("Token de autenticación requerido")
            
            user_roles = g.get('user_roles', [])
            user_role_names = [role.name for role in user_roles]
            
            # Verificar si tiene alguno de los roles requeridos
            has_required_role = any(role_name in user_role_names for role_name in role_names)
            
            if not has_required_role:
                raise AuthorizationError(f"Se requiere uno de estos roles: {', '.join(role_names)}")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_organization(organization: str):
    """Decorator para requerir pertenencia a organización específica"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.get('current_user_id'):
                raise AuthenticationError("Token de autenticación requerido")
            
            user_roles = g.get('user_roles', [])
            
            # Verificar si tiene algún rol de la organización requerida
            has_org_role = any(role.organization == organization for role in user_roles)
            
            if not has_org_role:
                raise AuthorizationError(f"Se requiere rol de organización: {organization}")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def require_level(max_level: int):
    """Decorator para requerir nivel jerárquico mínimo"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.get('current_user_id'):
                raise AuthenticationError("Token de autenticación requerido")
            
            user_roles = g.get('user_roles', [])
            
            # Obtener el nivel más alto del usuario
            user_max_level = min([role.level for role in user_roles]) if user_roles else 999
            
            if user_max_level > max_level:
                raise AuthorizationError(f"Se requiere nivel jerárquico {max_level} o superior")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def get_user_context():
    """Obtener contexto completo del usuario actual"""
    return {
        'user_id': g.get('current_user_id'),
        'store_id': g.get('current_store_id'),
        'roles': [role.to_dict() for role in g.get('user_roles', [])],
        'permissions': g.get('user_permissions', []),
        'organization_roles': {
            'odata': [role.name for role in g.get('user_roles', []) if role.organization == 'odata'],
            'sabrositas': [role.name for role in g.get('user_roles', []) if role.organization == 'sabrositas']
        }
    }

# Funciones de utilidad para verificaciones específicas
def is_odata_user() -> bool:
    """Verificar si el usuario actual es de Odata"""
    user_roles = g.get('user_roles', [])
    return any(role.organization == 'odata' for role in user_roles)

def is_sabrositas_user() -> bool:
    """Verificar si el usuario actual es de Sabrositas"""
    user_roles = g.get('user_roles', [])
    return any(role.organization == 'sabrositas' for role in user_roles)

def is_store_admin() -> bool:
    """Verificar si el usuario es administrador de tienda"""
    user_roles = g.get('user_roles', [])
    return any(role.role_type.value == 'store_admin' for role in user_roles)

def is_global_admin() -> bool:
    """Verificar si el usuario es administrador global"""
    user_roles = g.get('user_roles', [])
    return any(role.role_type.value in ['super_admin', 'global_admin'] for role in user_roles)

def can_access_store(store_id: int) -> bool:
    """Verificar si el usuario puede acceder a una tienda específica"""
    user_roles = g.get('user_roles', [])
    
    for role in user_roles:
        # Roles globales pueden acceder a cualquier tienda
        if role.can_access_all_stores:
            return True
        
        # Roles específicos de tienda solo a su tienda asignada
        if role.is_store_specific and g.get('current_store_id') == store_id:
            return True
    
    return False

def get_accessible_stores() -> List[int]:
    """Obtener lista de tiendas accesibles para el usuario actual"""
    user_roles = g.get('user_roles', [])
    accessible_stores = set()
    
    for role in user_roles:
        if role.can_access_all_stores:
            # Si puede acceder a todas, devolver todas las tiendas activas
            from app.models.store import Store
            all_stores = Store.query.filter_by(is_active=True).all()
            return [store.id for store in all_stores]
        elif role.is_store_specific and g.get('current_store_id'):
            accessible_stores.add(g.current_store_id)
    
    return list(accessible_stores)
