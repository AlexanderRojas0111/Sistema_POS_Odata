"""
IAM Service - Sistema Sabrositas POS
====================================
Servicio de gestión de identidades, roles y permisos
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
from app import db
from app.models.role import Role, Permission, UserRole, RoleType, PermissionCategory
from app.models.user import User
from app.exceptions import ValidationError, BusinessLogicError, AuthorizationError
import json

logger = logging.getLogger(__name__)

class IAMService:
    """Servicio de gestión de identidades y accesos"""
    
    def __init__(self):
        self.permission_matrix = self._load_permission_matrix()
    
    def _load_permission_matrix(self) -> Dict[str, List[str]]:
        """Cargar matriz de permisos por rol"""
        return {
            # ROLES ODATA (Tecnología)
            'super_admin': [
                'system:*:*',  # Acceso total al sistema
                'users:*:*',   # Gestión completa de usuarios
                'roles:*:*',   # Gestión completa de roles
                'stores:*:*',  # Gestión completa de tiendas
                'products:*:*', # Gestión completa de productos
                'inventory:*:*', # Gestión completa de inventario
                'sales:*:*',   # Gestión completa de ventas
                'reports:*:*', # Acceso a todos los reportes
                'auditing:*:*' # Acceso completo a auditoría
            ],
            
            'tech_admin': [
                'system:configuration:read',
                'system:configuration:write',
                'system:modules:read',
                'system:modules:write',
                'system:integrations:read',
                'system:integrations:write',
                'users:roles:read',
                'users:roles:write',
                'users:permissions:read',
                'users:permissions:write',
                'stores:configuration:read',
                'stores:configuration:write',
                'products:catalog:read',
                'products:catalog:write',
                'reports:technical:read',
                'auditing:logs:read'
            ],
            
            'tech_support': [
                'system:health:read',
                'users:support:read',
                'users:support:write',
                'users:tickets:read',
                'users:tickets:write',
                'stores:onboarding:read',
                'stores:onboarding:write',
                'products:support:read',
                'reports:support:read',
                'auditing:incidents:read'
            ],
            
            # ROLES CLIENTE (Sabrositas)
            'business_owner': [
                'reports:strategic:read',
                'reports:financial:read',
                'reports:analytics:read',
                'stores:performance:read',
                'sales:global:read',
                'inventory:global:read',
                'users:overview:read'
            ],
            
            'global_admin': [
                'stores:management:read',
                'stores:management:write',
                'inventory:global:read',
                'inventory:global:write',
                'inventory:transfers:read',
                'inventory:transfers:write',
                'products:catalog:read',
                'products:catalog:write',
                'purchases:global:read',
                'purchases:global:write',
                'sales:global:read',
                'reports:consolidated:read',
                'users:store_admins:read',
                'users:store_admins:write'
            ],
            
            'store_admin': [
                'inventory:store:read',
                'inventory:store:write',
                'inventory:adjustments:read',
                'inventory:adjustments:write',
                'products:store:read',
                'products:store:write',
                'purchases:store:read',
                'purchases:store:write',
                'sales:store:read',
                'sales:reports:read',
                'users:store:read',
                'users:store:write',
                'reports:store:read',
                'payments:store:read'
            ],
            
            'supervisor': [
                'inventory:store:read',
                'sales:store:read',
                'sales:validation:read',
                'purchases:store:read',
                'reports:audit:read',
                'reports:store:read',
                'users:store:read',
                'payments:validation:read'
            ],
            
            'cashier': [
                'sales:register:read',
                'sales:register:write',
                'sales:payments:read',
                'sales:payments:write',
                'sales:receipts:read',
                'sales:receipts:write',
                'sales:refunds:read',
                'sales:refunds:write',
                'inventory:products:read',
                'reports:cashier:read'
            ],
            
            'waiter': [
                'sales:orders:read',
                'sales:orders:write',
                'inventory:products:read',
                'kitchen:orders:read',
                'kitchen:orders:write',
                'kitchen:status:read'
            ],
            
            'kitchen': [
                'kitchen:orders:read',
                'kitchen:orders:write',
                'kitchen:status:read',
                'kitchen:status:write',
                'inventory:products:read',
                'inventory:consumption:read'
            ],
            
            'purchasing': [
                'purchases:store:read',
                'purchases:store:write',
                'purchases:suppliers:read',
                'purchases:suppliers:write',
                'inventory:receiving:read',
                'inventory:receiving:write',
                'reports:purchasing:read'
            ]
        }
    
    def initialize_system_roles(self) -> bool:
        """Inicializar roles del sistema"""
        try:
            roles_data = [
                # ROLES ODATA
                {
                    'name': 'super_admin',
                    'display_name': 'SuperAdmin Odata',
                    'description': 'Control global y emergencias del sistema',
                    'role_type': RoleType.SUPER_ADMIN,
                    'organization': 'odata',
                    'level': 1,
                    'is_system_role': True,
                    'max_users': 2,
                    'requires_approval': True,
                    'can_access_all_stores': True
                },
                {
                    'name': 'tech_admin',
                    'display_name': 'Administrador Técnico Odata',
                    'description': 'Parametrización, desarrollo y ajustes del sistema',
                    'role_type': RoleType.TECH_ADMIN,
                    'organization': 'odata',
                    'level': 2,
                    'is_system_role': True,
                    'max_users': 5,
                    'requires_approval': True,
                    'can_access_all_stores': True
                },
                {
                    'name': 'tech_support',
                    'display_name': 'Soporte Técnico Odata',
                    'description': 'Atención de incidencias y capacitación',
                    'role_type': RoleType.TECH_SUPPORT,
                    'organization': 'odata',
                    'level': 3,
                    'is_system_role': True,
                    'max_users': 10,
                    'can_access_all_stores': True
                },
                
                # ROLES CLIENTE SABROSITAS
                {
                    'name': 'business_owner',
                    'display_name': 'Dueño de Negocio',
                    'description': 'Nivel estratégico, análisis y resultados globales',
                    'role_type': RoleType.BUSINESS_OWNER,
                    'organization': 'sabrositas',
                    'level': 1,
                    'is_system_role': True,
                    'max_users': 3,
                    'requires_approval': True,
                    'can_access_all_stores': True
                },
                {
                    'name': 'global_admin',
                    'display_name': 'Administrador Global',
                    'description': 'Control operativo global de todas las tiendas',
                    'role_type': RoleType.GLOBAL_ADMIN,
                    'organization': 'sabrositas',
                    'level': 2,
                    'is_system_role': True,
                    'max_users': 5,
                    'requires_approval': True,
                    'can_access_all_stores': True
                },
                {
                    'name': 'store_admin',
                    'display_name': 'Administrador de Tienda',
                    'description': 'Control operativo de inventario, compras y usuarios de tienda',
                    'role_type': RoleType.STORE_ADMIN,
                    'organization': 'sabrositas',
                    'level': 3,
                    'is_system_role': True,
                    'is_store_specific': True,
                    'can_access_all_stores': False
                },
                {
                    'name': 'supervisor',
                    'display_name': 'Supervisor/Auditor',
                    'description': 'Validación de procesos y control de calidad',
                    'role_type': RoleType.SUPERVISOR,
                    'organization': 'sabrositas',
                    'level': 4,
                    'is_system_role': True,
                    'is_store_specific': True,
                    'can_access_all_stores': False
                },
                {
                    'name': 'cashier',
                    'display_name': 'Cajero',
                    'description': 'Responsable de caja y registro de ventas',
                    'role_type': RoleType.CASHIER,
                    'organization': 'sabrositas',
                    'level': 5,
                    'is_system_role': True,
                    'is_store_specific': True,
                    'can_access_all_stores': False
                },
                {
                    'name': 'waiter',
                    'display_name': 'Vendedor/Mesero',
                    'description': 'Atención al cliente y registro de pedidos',
                    'role_type': RoleType.WAITER,
                    'organization': 'sabrositas',
                    'level': 6,
                    'is_system_role': True,
                    'is_store_specific': True,
                    'can_access_all_stores': False
                },
                {
                    'name': 'kitchen',
                    'display_name': 'Cocina/Producción',
                    'description': 'Preparación de pedidos y gestión de cocina',
                    'role_type': RoleType.KITCHEN,
                    'organization': 'sabrositas',
                    'level': 6,
                    'is_system_role': True,
                    'is_store_specific': True,
                    'can_access_all_stores': False
                },
                {
                    'name': 'purchasing',
                    'display_name': 'Compras/Abastecimiento',
                    'description': 'Control de proveedores y compras',
                    'role_type': RoleType.PURCHASING,
                    'organization': 'sabrositas',
                    'level': 5,
                    'is_system_role': True,
                    'is_store_specific': True,
                    'can_access_all_stores': False
                }
            ]
            
            created_count = 0
            for role_data in roles_data:
                existing_role = Role.query.filter_by(name=role_data['name']).first()
                if not existing_role:
                    role = Role(**role_data)
                    db.session.add(role)
                    created_count += 1
                    logger.info(f"Rol del sistema creado: {role_data['name']}")
            
            if created_count > 0:
                db.session.commit()
                logger.info(f"Inicialización de roles completada: {created_count} roles creados")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inicializando roles del sistema: {e}")
            return False
    
    def initialize_system_permissions(self) -> bool:
        """Inicializar permisos del sistema"""
        try:
            permissions_data = []
            
            # Generar permisos basados en la matriz
            for role_name, permission_patterns in self.permission_matrix.items():
                for pattern in permission_patterns:
                    if pattern == 'system:*:*':
                        # Expandir permisos de sistema
                        system_perms = [
                            ('system', 'configuration', 'read'),
                            ('system', 'configuration', 'write'),
                            ('system', 'modules', 'read'),
                            ('system', 'modules', 'write'),
                            ('system', 'health', 'read'),
                            ('system', 'integrations', 'read'),
                            ('system', 'integrations', 'write')
                        ]
                        permissions_data.extend(system_perms)
                    elif ':*:*' in pattern:
                        # Expandir permisos completos por categoría
                        category = pattern.split(':')[0]
                        category_perms = self._expand_category_permissions(category)
                        permissions_data.extend(category_perms)
                    else:
                        # Permiso específico
                        parts = pattern.split(':')
                        if len(parts) == 3:
                            permissions_data.append((parts[0], parts[1], parts[2]))
            
            # Eliminar duplicados
            unique_permissions = list(set(permissions_data))
            
            created_count = 0
            for category, resource, action in unique_permissions:
                permission_name = f"{category}:{resource}:{action}"
                
                existing_permission = Permission.query.filter_by(name=permission_name).first()
                if not existing_permission:
                    permission = Permission(
                        name=permission_name,
                        display_name=f"{action.title()} {resource.title()}",
                        description=f"Permiso para {action} en {resource}",
                        category=PermissionCategory(category),
                        resource=resource,
                        action=action,
                        is_system_permission=True
                    )
                    db.session.add(permission)
                    created_count += 1
            
            if created_count > 0:
                db.session.commit()
                logger.info(f"Inicialización de permisos completada: {created_count} permisos creados")
            
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error inicializando permisos del sistema: {e}")
            return False
    
    def _expand_category_permissions(self, category: str) -> List[Tuple[str, str, str]]:
        """Expandir permisos por categoría"""
        expansions = {
            'users': [
                ('users', 'profile', 'read'),
                ('users', 'profile', 'write'),
                ('users', 'roles', 'read'),
                ('users', 'roles', 'write'),
                ('users', 'permissions', 'read'),
                ('users', 'store', 'read'),
                ('users', 'store', 'write')
            ],
            'products': [
                ('products', 'catalog', 'read'),
                ('products', 'catalog', 'write'),
                ('products', 'store', 'read'),
                ('products', 'store', 'write'),
                ('products', 'prices', 'read'),
                ('products', 'prices', 'write')
            ],
            'inventory': [
                ('inventory', 'store', 'read'),
                ('inventory', 'store', 'write'),
                ('inventory', 'global', 'read'),
                ('inventory', 'global', 'write'),
                ('inventory', 'transfers', 'read'),
                ('inventory', 'transfers', 'write'),
                ('inventory', 'adjustments', 'read'),
                ('inventory', 'adjustments', 'write')
            ],
            'sales': [
                ('sales', 'register', 'read'),
                ('sales', 'register', 'write'),
                ('sales', 'orders', 'read'),
                ('sales', 'orders', 'write'),
                ('sales', 'payments', 'read'),
                ('sales', 'payments', 'write'),
                ('sales', 'refunds', 'read'),
                ('sales', 'refunds', 'write'),
                ('sales', 'store', 'read'),
                ('sales', 'global', 'read')
            ],
            'reports': [
                ('reports', 'strategic', 'read'),
                ('reports', 'financial', 'read'),
                ('reports', 'analytics', 'read'),
                ('reports', 'store', 'read'),
                ('reports', 'consolidated', 'read'),
                ('reports', 'audit', 'read')
            ]
        }
        
        return expansions.get(category, [(category, 'general', 'read')])
    
    def assign_role_to_user(self, 
                           user_id: int, 
                           role_id: int, 
                           assigned_by_user_id: int,
                           store_id: int = None,
                           is_primary: bool = False,
                           valid_until: datetime = None) -> UserRole:
        """Asignar rol a usuario"""
        try:
            # Validar usuario existe
            user = User.query.get(user_id)
            if not user:
                raise ValidationError(f"Usuario no encontrado: {user_id}")
            
            # Validar rol existe
            role = Role.query.get(role_id)
            if not role:
                raise ValidationError(f"Rol no encontrado: {role_id}")
            
            # Validar usuario asignador tiene permisos
            assigner = User.query.get(assigned_by_user_id)
            if not assigner:
                raise ValidationError(f"Usuario asignador no encontrado: {assigned_by_user_id}")
            
            # Verificar si el usuario asignador puede asignar este rol
            if not self.can_user_assign_role(assigned_by_user_id, role_id):
                raise AuthorizationError(f"Usuario {assigned_by_user_id} no puede asignar rol {role.name}")
            
            # Verificar límite máximo de usuarios para el rol
            if role.max_users:
                current_users = UserRole.query.filter_by(
                    role_id=role_id,
                    is_active=True
                ).count()
                
                if current_users >= role.max_users:
                    raise BusinessLogicError(f"Rol {role.name} ha alcanzado el límite máximo de {role.max_users} usuarios")
            
            # Verificar si ya existe asignación activa
            existing_assignment = UserRole.query.filter_by(
                user_id=user_id,
                role_id=role_id,
                store_id=store_id,
                is_active=True
            ).first()
            
            if existing_assignment:
                raise BusinessLogicError(f"Usuario ya tiene el rol {role.name} asignado")
            
            # Si es rol primario, desactivar otros roles primarios
            if is_primary:
                UserRole.query.filter_by(
                    user_id=user_id,
                    is_primary=True,
                    is_active=True
                ).update({'is_primary': False})
            
            # Crear asignación
            user_role = UserRole(
                user_id=user_id,
                role_id=role_id,
                store_id=store_id,
                is_primary=is_primary,
                assigned_by=assigned_by_user_id,
                valid_until=valid_until
            )
            
            db.session.add(user_role)
            db.session.commit()
            
            logger.info(f"Rol {role.name} asignado a usuario {user_id} por {assigned_by_user_id}")
            return user_role
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error asignando rol: {e}")
            raise
    
    def can_user_assign_role(self, user_id: int, target_role_id: int) -> bool:
        """Verificar si un usuario puede asignar un rol específico"""
        try:
            user_roles = self.get_user_roles(user_id)
            target_role = Role.query.get(target_role_id)
            
            if not target_role:
                return False
            
            # SuperAdmin puede asignar cualquier rol
            if any(role.role_type == RoleType.SUPER_ADMIN for role in user_roles):
                return True
            
            # Administradores técnicos pueden asignar roles no críticos
            if any(role.role_type == RoleType.TECH_ADMIN for role in user_roles):
                return target_role.level >= 3  # No puede asignar SuperAdmin ni TechAdmin
            
            # Administradores globales pueden asignar roles de tienda
            if any(role.role_type == RoleType.GLOBAL_ADMIN for role in user_roles):
                return target_role.organization == 'sabrositas' and target_role.level >= 3
            
            # Administradores de tienda pueden asignar roles operativos
            if any(role.role_type == RoleType.STORE_ADMIN for role in user_roles):
                return target_role.level >= 5 and target_role.is_store_specific
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando permisos de asignación: {e}")
            return False
    
    def get_user_roles(self, user_id: int, store_id: int = None) -> List[Role]:
        """Obtener roles activos de un usuario"""
        try:
            query = db.session.query(Role).join(UserRole).filter(
                UserRole.user_id == user_id,
                UserRole.is_active == True,
                Role.is_active == True
            )
            
            # Filtrar por tienda si se especifica
            if store_id:
                query = query.filter(
                    (UserRole.store_id == store_id) | 
                    (UserRole.store_id.is_(None)) |
                    (Role.can_access_all_stores == True)
                )
            
            return query.all()
            
        except Exception as e:
            logger.error(f"Error obteniendo roles de usuario {user_id}: {e}")
            return []
    
    def get_user_permissions(self, user_id: int, store_id: int = None) -> List[str]:
        """Obtener permisos efectivos de un usuario"""
        try:
            user_roles = self.get_user_roles(user_id, store_id)
            all_permissions = set()
            
            for role in user_roles:
                role_permissions = self.permission_matrix.get(role.name, [])
                all_permissions.update(role_permissions)
            
            return list(all_permissions)
            
        except Exception as e:
            logger.error(f"Error obteniendo permisos de usuario {user_id}: {e}")
            return []
    
    def has_permission(self, user_id: int, permission: str, store_id: int = None) -> bool:
        """Verificar si un usuario tiene un permiso específico"""
        try:
            user_permissions = self.get_user_permissions(user_id, store_id)
            
            # Verificar permiso exacto
            if permission in user_permissions:
                return True
            
            # Verificar permisos wildcard
            for user_perm in user_permissions:
                if self._matches_wildcard_permission(permission, user_perm):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error verificando permiso {permission} para usuario {user_id}: {e}")
            return False
    
    def _matches_wildcard_permission(self, requested: str, granted: str) -> bool:
        """Verificar si un permiso coincide con un patrón wildcard"""
        if '*' not in granted:
            return requested == granted
        
        req_parts = requested.split(':')
        grant_parts = granted.split(':')
        
        if len(req_parts) != len(grant_parts):
            return False
        
        for req_part, grant_part in zip(req_parts, grant_parts):
            if grant_part != '*' and req_part != grant_part:
                return False
        
        return True
    
    def get_role_hierarchy(self) -> Dict[str, Any]:
        """Obtener jerarquía completa de roles"""
        try:
            roles = Role.query.filter_by(is_active=True).order_by(Role.level, Role.name).all()
            
            hierarchy = {
                'odata_roles': [],
                'sabrositas_roles': []
            }
            
            for role in roles:
                role_data = role.to_dict(include_permissions=True)
                
                if role.organization == 'odata':
                    hierarchy['odata_roles'].append(role_data)
                else:
                    hierarchy['sabrositas_roles'].append(role_data)
            
            return hierarchy
            
        except Exception as e:
            logger.error(f"Error obteniendo jerarquía de roles: {e}")
            return {'odata_roles': [], 'sabrositas_roles': []}
