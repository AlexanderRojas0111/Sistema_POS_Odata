"""
Roles API v1 - Sistema IAM Sabrositas
=====================================
APIs para gestión de roles, permisos y asignaciones
"""

from flask import Blueprint, request, jsonify, g
from app import db
from app.services.iam_service import IAMService
from app.services.auth_service import AuthService
from app.middleware.rbac_middleware import (
    require_permission, require_role, require_organization, 
    require_level, get_user_context
)
from app.exceptions import ValidationError, BusinessLogicError, AuthorizationError
import logging

logger = logging.getLogger(__name__)

# Blueprint para APIs de roles
roles_bp = Blueprint('roles', __name__)

# Inicializar servicios
iam_service = IAMService()
auth_service = AuthService()

@roles_bp.route('/roles', methods=['GET'])
# @require_permission('users:roles:read')  # Temporalmente deshabilitado para testing
def get_all_roles():
    """Obtener todos los roles del sistema"""
    try:
        organization = request.args.get('organization')  # 'odata' o 'sabrositas'
        include_permissions = request.args.get('include_permissions', 'false').lower() == 'true'
        
        hierarchy = iam_service.get_role_hierarchy()
        
        if organization:
            if organization == 'odata':
                roles = hierarchy['odata_roles']
            elif organization == 'sabrositas':
                roles = hierarchy['sabrositas_roles']
            else:
                return jsonify({
                    'status': 'error',
                    'message': 'Organización debe ser "odata" o "sabrositas"'
                }), 400
        else:
            roles = hierarchy['odata_roles'] + hierarchy['sabrositas_roles']
        
        return jsonify({
            'status': 'success',
            'data': {
                'roles': roles,
                'total': len(roles),
                'filter_organization': organization,
                'include_permissions': include_permissions
            }
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo roles: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo roles',
            'error': str(e)
        }), 500

@roles_bp.route('/roles/<int:role_id>', methods=['GET'])
# @require_permission('users:roles:read')  # Temporalmente deshabilitado para testing
def get_role(role_id):
    """Obtener rol específico por ID"""
    try:
        from app.models.role import Role
        
        role = Role.query.get(role_id)
        if not role:
            return jsonify({
                'status': 'error',
                'message': 'Rol no encontrado'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': {'role': role.to_dict(include_permissions=True)}
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo rol {role_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo rol',
            'error': str(e)
        }), 500

@roles_bp.route('/users/<int:user_id>/roles', methods=['GET'])
@require_permission('users:roles:read')
def get_user_roles(user_id):
    """Obtener roles de un usuario específico"""
    try:
        store_id = request.args.get('store_id', type=int)
        user_roles = iam_service.get_user_roles(user_id, store_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'user_id': user_id,
                'store_id': store_id,
                'roles': [role.to_dict() for role in user_roles],
                'total_roles': len(user_roles)
            }
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo roles de usuario {user_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo roles de usuario',
            'error': str(e)
        }), 500

@roles_bp.route('/users/<int:user_id>/permissions', methods=['GET'])
@require_permission('users:permissions:read')
def get_user_permissions(user_id):
    """Obtener permisos efectivos de un usuario"""
    try:
        store_id = request.args.get('store_id', type=int)
        permissions = iam_service.get_user_permissions(user_id, store_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'user_id': user_id,
                'store_id': store_id,
                'permissions': permissions,
                'total_permissions': len(permissions)
            }
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo permisos de usuario {user_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo permisos de usuario',
            'error': str(e)
        }), 500

@roles_bp.route('/users/<int:user_id>/roles', methods=['POST'])
@require_permission('users:roles:write')
def assign_role_to_user(user_id):
    """Asignar rol a usuario"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos requeridos'
            }), 400
        
        role_id = data.get('role_id')
        store_id = data.get('store_id')
        is_primary = data.get('is_primary', False)
        valid_until = data.get('valid_until')
        
        if not role_id:
            return jsonify({
                'status': 'error',
                'message': 'role_id requerido'
            }), 400
        
        # Parsear fecha de expiración si se proporciona
        if valid_until:
            from datetime import datetime
            try:
                valid_until = datetime.fromisoformat(valid_until)
            except ValueError:
                return jsonify({
                    'status': 'error',
                    'message': 'Formato de fecha inválido para valid_until'
                }), 400
        
        # Asignar rol
        user_role = iam_service.assign_role_to_user(
            user_id=user_id,
            role_id=role_id,
            assigned_by_user_id=g.current_user_id,
            store_id=store_id,
            is_primary=is_primary,
            valid_until=valid_until
        )
        
        return jsonify({
            'status': 'success',
            'message': f'Rol asignado exitosamente',
            'data': {'user_role': user_role.to_dict()}
        }), 201
    
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    
    except AuthorizationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 403
    
    except BusinessLogicError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 422
    
    except Exception as e:
        logger.error(f"Error asignando rol a usuario {user_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error asignando rol',
            'error': str(e)
        }), 500

@roles_bp.route('/users/<int:user_id>/roles/<int:role_id>', methods=['DELETE'])
@require_permission('users:roles:write')
def revoke_role_from_user(user_id, role_id):
    """Revocar rol de usuario"""
    try:
        data = request.get_json() or {}
        reason = data.get('reason', 'Revocado por administrador')
        store_id = data.get('store_id')
        
        from app.models.role import UserRole
        
        # Buscar asignación activa
        query = UserRole.query.filter_by(
            user_id=user_id,
            role_id=role_id,
            is_active=True
        )
        
        if store_id:
            query = query.filter_by(store_id=store_id)
        
        user_role = query.first()
        
        if not user_role:
            return jsonify({
                'status': 'error',
                'message': 'Asignación de rol no encontrada'
            }), 404
        
        # Revocar rol
        user_role.revoke(g.current_user_id, reason)
        db.session.commit()
        
        logger.info(f"Rol {role_id} revocado de usuario {user_id} por {g.current_user_id}")
        
        return jsonify({
            'status': 'success',
            'message': 'Rol revocado exitosamente',
            'data': {
                'user_id': user_id,
                'role_id': role_id,
                'revoked_at': user_role.revoked_at.isoformat(),
                'reason': reason
            }
        })
    
    except Exception as e:
        logger.error(f"Error revocando rol: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error revocando rol',
            'error': str(e)
        }), 500

@roles_bp.route('/permissions/check', methods=['POST'])
def check_permission():
    """Verificar si el usuario actual tiene un permiso específico"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos requeridos'
            }), 400
        
        permission = data.get('permission')
        store_id = data.get('store_id')
        
        if not permission:
            return jsonify({
                'status': 'error',
                'message': 'permission requerido'
            }), 400
        
        if not g.get('current_user_id'):
            return jsonify({
                'status': 'error',
                'message': 'Usuario no autenticado'
            }), 401
        
        has_permission = iam_service.has_permission(
            g.current_user_id,
            permission,
            store_id
        )
        
        return jsonify({
            'status': 'success',
            'data': {
                'user_id': g.current_user_id,
                'permission': permission,
                'store_id': store_id,
                'has_permission': has_permission
            }
        })
    
    except Exception as e:
        logger.error(f"Error verificando permiso: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error verificando permiso',
            'error': str(e)
        }), 500

@roles_bp.route('/users/context', methods=['GET'])
def get_current_user_context():
    """Obtener contexto completo del usuario actual"""
    try:
        if not g.get('current_user_id'):
            return jsonify({
                'status': 'error',
                'message': 'Usuario no autenticado'
            }), 401
        
        context = get_user_context()
        
        return jsonify({
            'status': 'success',
            'data': context
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo contexto de usuario: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo contexto de usuario',
            'error': str(e)
        }), 500

@roles_bp.route('/roles/hierarchy', methods=['GET'])
@require_permission('users:roles:read')
def get_role_hierarchy():
    """Obtener jerarquía completa de roles"""
    try:
        hierarchy = iam_service.get_role_hierarchy()
        
        return jsonify({
            'status': 'success',
            'data': hierarchy
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo jerarquía de roles: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo jerarquía de roles',
            'error': str(e)
        }), 500

@roles_bp.route('/permissions/matrix', methods=['GET'])
@require_level(2)  # Solo roles de nivel 2 o superior
def get_permission_matrix():
    """Obtener matriz completa de permisos"""
    try:
        return jsonify({
            'status': 'success',
            'data': {
                'permission_matrix': iam_service.permission_matrix,
                'role_descriptions': {
                    # ODATA Roles
                    'super_admin': 'Control global y emergencias del sistema',
                    'tech_admin': 'Parametrización, desarrollo y ajustes',
                    'tech_support': 'Atención de incidencias y capacitación',
                    
                    # Sabrositas Roles
                    'business_owner': 'Nivel estratégico, análisis y resultados globales',
                    'global_admin': 'Control operativo global de todas las tiendas',
                    'store_admin': 'Control operativo de inventario, compras y usuarios de tienda',
                    'supervisor': 'Validación de procesos y control de calidad',
                    'cashier': 'Responsable de caja y registro de ventas',
                    'waiter': 'Atención al cliente y registro de pedidos',
                    'kitchen': 'Preparación de pedidos y gestión de cocina',
                    'purchasing': 'Control de proveedores y compras'
                }
            }
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo matriz de permisos: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo matriz de permisos',
            'error': str(e)
        }), 500

@roles_bp.route('/roles/initialize', methods=['POST'])
@require_role('super_admin')
def initialize_system_roles():
    """Inicializar roles y permisos del sistema"""
    try:
        # Inicializar roles
        roles_success = iam_service.initialize_system_roles()
        
        # Inicializar permisos
        permissions_success = iam_service.initialize_system_permissions()
        
        if roles_success and permissions_success:
            return jsonify({
                'status': 'success',
                'message': 'Roles y permisos del sistema inicializados exitosamente',
                'data': {
                    'roles_initialized': roles_success,
                    'permissions_initialized': permissions_success
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error inicializando sistema de roles',
                'data': {
                    'roles_initialized': roles_success,
                    'permissions_initialized': permissions_success
                }
            }), 500
    
    except Exception as e:
        logger.error(f"Error inicializando sistema de roles: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error inicializando sistema de roles',
            'error': str(e)
        }), 500

# Endpoint para simular flujos de trabajo por rol
@roles_bp.route('/roles/simulate/<role_name>', methods=['GET'])
@require_level(2)
def simulate_role_workflow(role_name):
    """Simular flujo de trabajo de un rol específico"""
    try:
        workflows = {
            'cashier': {
                'description': 'Flujo de trabajo típico de un cajero',
                'steps': [
                    'Iniciar sesión en el sistema',
                    'Verificar productos disponibles',
                    'Registrar venta de productos',
                    'Procesar pago (efectivo/tarjeta)',
                    'Emitir comprobante',
                    'Actualizar inventario automáticamente',
                    'Generar reporte de caja al final del día'
                ],
                'permissions_required': [
                    'sales:register:read',
                    'sales:register:write',
                    'sales:payments:write',
                    'sales:receipts:write',
                    'inventory:products:read',
                    'reports:cashier:read'
                ]
            },
            
            'store_admin': {
                'description': 'Flujo de trabajo de administrador de tienda',
                'steps': [
                    'Revisar inventario y stock mínimo',
                    'Generar pedido automático a fábrica',
                    'Registrar compras a proveedores locales',
                    'Validar entregas y actualizar inventario',
                    'Gestionar usuarios de la tienda',
                    'Revisar ventas del día',
                    'Realizar cierre diario (22:00 hrs)',
                    'Generar reportes de la tienda'
                ],
                'permissions_required': [
                    'inventory:store:read',
                    'inventory:store:write',
                    'purchases:store:write',
                    'users:store:write',
                    'sales:store:read',
                    'reports:store:read'
                ]
            },
            
            'business_owner': {
                'description': 'Flujo de trabajo del dueño del negocio',
                'steps': [
                    'Revisar tablero estratégico',
                    'Analizar ventas por tienda y región',
                    'Evaluar indicadores clave (KPIs)',
                    'Revisar reportes financieros consolidados',
                    'Analizar punto de equilibrio por tienda',
                    'Tomar decisiones estratégicas basadas en datos'
                ],
                'permissions_required': [
                    'reports:strategic:read',
                    'reports:financial:read',
                    'reports:analytics:read',
                    'stores:performance:read',
                    'sales:global:read'
                ]
            },
            
            'kitchen': {
                'description': 'Flujo de trabajo de cocina/producción',
                'steps': [
                    'Visualizar pedidos pendientes',
                    'Verificar disponibilidad de ingredientes',
                    'Marcar pedido como "En preparación"',
                    'Preparar arepa según especificaciones',
                    'Marcar pedido como "Listo"',
                    'Notificar al mesero/cajero',
                    'Confirmar entrega del pedido'
                ],
                'permissions_required': [
                    'kitchen:orders:read',
                    'kitchen:orders:write',
                    'kitchen:status:write',
                    'inventory:products:read'
                ]
            }
        }
        
        workflow = workflows.get(role_name)
        if not workflow:
            return jsonify({
                'status': 'error',
                'message': f'Simulación no disponible para rol: {role_name}'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': {
                'role_name': role_name,
                'workflow': workflow
            }
        })
    
    except Exception as e:
        logger.error(f"Error simulando workflow para rol {role_name}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error simulando workflow',
            'error': str(e)
        }), 500

# Health check del sistema IAM
@roles_bp.route('/iam/health', methods=['GET'])
def iam_health():
    """Health check del sistema IAM"""
    try:
        from app.models.role import Role, Permission
        
        total_roles = Role.query.filter_by(is_active=True).count()
        total_permissions = Permission.query.filter_by(is_active=True).count()
        odata_roles = Role.query.filter_by(organization='odata', is_active=True).count()
        sabrositas_roles = Role.query.filter_by(organization='sabrositas', is_active=True).count()
        
        return jsonify({
            'service': 'iam-system',
            'status': 'healthy',
            'data': {
                'total_roles': total_roles,
                'total_permissions': total_permissions,
                'odata_roles': odata_roles,
                'sabrositas_roles': sabrositas_roles,
                'system_initialized': total_roles > 0 and total_permissions > 0
            }
        })
    
    except Exception as e:
        logger.error(f"Error en health check IAM: {str(e)}")
        return jsonify({
            'service': 'iam-system',
            'status': 'unhealthy',
            'error': str(e)
        }), 503
