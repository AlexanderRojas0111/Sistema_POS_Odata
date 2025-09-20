"""
Store API v1 - Sistema Multi-Sede Sabrositas
============================================
APIs para gestión de tiendas, inventario multi-sede y transferencias.
"""

from flask import Blueprint, request, jsonify, current_app
from app.services.store_service import StoreService
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import require_auth, require_role
from app.exceptions import ValidationError, BusinessLogicError
import logging

logger = logging.getLogger(__name__)

# Blueprint para APIs de tiendas
stores_bp = Blueprint('stores', __name__)

# Inicializar servicios
store_service = StoreService()
auth_service = AuthService()

@stores_bp.route('/stores', methods=['GET'])
@require_auth
def get_all_stores():
    """Obtener todas las tiendas"""
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        stores = store_service.get_all_stores(include_inactive=include_inactive)
        
        return jsonify({
            'status': 'success',
            'data': {
                'stores': [store.to_dict() for store in stores],
                'total': len(stores)
            }
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo tiendas: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo tiendas',
            'error': str(e)
        }), 500

@stores_bp.route('/stores', methods=['POST'])
@require_auth
@require_role('manager')
def create_store():
    """Crear nueva tienda"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos requeridos'
            }), 400
        
        store = store_service.create_store(data)
        
        return jsonify({
            'status': 'success',
            'message': f'Tienda {store.name} creada exitosamente',
            'data': {'store': store.to_dict()}
        }), 201
    
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Error creando tienda: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error creando tienda',
            'error': str(e)
        }), 500

@stores_bp.route('/stores/<int:store_id>', methods=['GET'])
@require_auth
def get_store(store_id):
    """Obtener tienda por ID"""
    try:
        store = store_service.get_store_by_id(store_id)
        if not store:
            return jsonify({
                'status': 'error',
                'message': 'Tienda no encontrada'
            }), 404
        
        return jsonify({
            'status': 'success',
            'data': {'store': store.to_dict()}
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo tienda {store_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo tienda',
            'error': str(e)
        }), 500

@stores_bp.route('/stores/<int:store_id>', methods=['PUT'])
@require_auth
@require_role('manager')
def update_store(store_id):
    """Actualizar tienda"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos requeridos'
            }), 400
        
        store = store_service.update_store(store_id, data)
        
        return jsonify({
            'status': 'success',
            'message': f'Tienda {store.name} actualizada exitosamente',
            'data': {'store': store.to_dict()}
        })
    
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Error actualizando tienda {store_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error actualizando tienda',
            'error': str(e)
        }), 500

@stores_bp.route('/stores/<int:store_id>/inventory', methods=['GET'])
@require_auth
def get_store_inventory(store_id):
    """Obtener inventario de una tienda"""
    try:
        include_inactive = request.args.get('include_inactive', 'false').lower() == 'true'
        inventory = store_service.get_store_inventory(store_id, include_inactive=include_inactive)
        
        return jsonify({
            'status': 'success',
            'data': {
                'store_id': store_id,
                'inventory': inventory,
                'total_products': len(inventory)
            }
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo inventario de tienda {store_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo inventario',
            'error': str(e)
        }), 500

@stores_bp.route('/stores/<int:store_id>/products/assign', methods=['POST'])
@require_auth
@require_role('manager')
def assign_products_to_store(store_id):
    """Asignar productos a una tienda"""
    try:
        data = request.get_json()
        if not data or not data.get('products'):
            return jsonify({
                'status': 'error',
                'message': 'Lista de productos requerida'
            }), 400
        
        success = store_service.assign_products_to_store(store_id, data['products'])
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Productos asignados exitosamente a la tienda',
                'data': {
                    'store_id': store_id,
                    'products_assigned': len(data['products'])
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error asignando productos'
            }), 500
    
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Error asignando productos a tienda {store_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error asignando productos',
            'error': str(e)
        }), 500

@stores_bp.route('/stores/<int:store_id>/products/sync-all', methods=['POST'])
@require_auth
@require_role('manager')
def sync_all_products_to_store(store_id):
    """Sincronizar todos los productos activos a una tienda"""
    try:
        success = store_service.sync_all_products_to_store(store_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Productos sincronizados exitosamente',
                'data': {'store_id': store_id}
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error sincronizando productos'
            }), 500
    
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Error sincronizando productos a tienda {store_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error sincronizando productos',
            'error': str(e)
        }), 500

@stores_bp.route('/stores/low-stock', methods=['GET'])
@require_auth
def get_low_stock_products():
    """Obtener productos con stock bajo en todas las tiendas"""
    try:
        store_id = request.args.get('store_id', type=int)
        low_stock = store_service.get_low_stock_products(store_id=store_id)
        
        return jsonify({
            'status': 'success',
            'data': {
                'low_stock_products': low_stock,
                'total': len(low_stock),
                'store_id': store_id
            }
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo productos con stock bajo: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo productos con stock bajo',
            'error': str(e)
        }), 500

@stores_bp.route('/inventory/consolidated', methods=['GET'])
@require_auth
@require_role('manager')
def get_consolidated_inventory():
    """Obtener inventario consolidado de todas las tiendas"""
    try:
        consolidated = store_service.get_consolidated_inventory()
        
        return jsonify({
            'status': 'success',
            'data': {
                'consolidated_inventory': consolidated,
                'total_products': len(consolidated)
            }
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo inventario consolidado: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo inventario consolidado',
            'error': str(e)
        }), 500

@stores_bp.route('/transfers', methods=['POST'])
@require_auth
def create_transfer():
    """Crear transferencia de inventario entre tiendas"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos requeridos'
            }), 400
        
        # Obtener usuario actual del token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_data = auth_service.decode_token(token)
        data['requested_by'] = user_data['user_id']
        
        transfer = store_service.create_transfer(data)
        
        return jsonify({
            'status': 'success',
            'message': f'Transferencia {transfer.transfer_number} creada exitosamente',
            'data': {'transfer': transfer.to_dict()}
        }), 201
    
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    
    except BusinessLogicError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 422
    
    except Exception as e:
        logger.error(f"Error creando transferencia: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error creando transferencia',
            'error': str(e)
        }), 500

@stores_bp.route('/stores/<int:store_id>/transfers', methods=['GET'])
@require_auth
def get_store_transfers(store_id):
    """Obtener transferencias de una tienda"""
    try:
        status = request.args.get('status')
        transfers = store_service.get_store_transfers(store_id, status=status)
        
        return jsonify({
            'status': 'success',
            'data': {
                'store_id': store_id,
                'transfers': [transfer.to_dict() for transfer in transfers],
                'total': len(transfers),
                'filter_status': status
            }
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo transferencias de tienda {store_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo transferencias',
            'error': str(e)
        }), 500

@stores_bp.route('/stores/<int:store_id>/metrics', methods=['GET'])
@require_auth
def get_store_metrics(store_id):
    """Obtener métricas de desempeño de una tienda"""
    try:
        days = request.args.get('days', default=30, type=int)
        metrics = store_service.get_store_performance_metrics(store_id, days=days)
        
        return jsonify({
            'status': 'success',
            'data': metrics
        })
    
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Error obteniendo métricas de tienda {store_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo métricas',
            'error': str(e)
        }), 500

@stores_bp.route('/stores/<int:store_id>/sync', methods=['POST'])
@require_auth
def update_store_sync(store_id):
    """Actualizar estado de sincronización de una tienda"""
    try:
        success = store_service.update_store_sync_status(store_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Estado de sincronización actualizado',
                'data': {
                    'store_id': store_id,
                    'sync_timestamp': 'updated'
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error actualizando sincronización'
            }), 500
    
    except Exception as e:
        logger.error(f"Error actualizando sincronización de tienda {store_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error actualizando sincronización',
            'error': str(e)
        }), 500

# Ruta de salud específica para multi-sede
@stores_bp.route('/stores/health', methods=['GET'])
def stores_health():
    """Health check para el sistema multi-sede"""
    try:
        stores = store_service.get_all_stores()
        active_stores = [s for s in stores if s.is_active]
        online_stores = [s for s in active_stores if s.is_online]
        
        return jsonify({
            'status': 'healthy',
            'service': 'multi-store-system',
            'data': {
                'total_stores': len(stores),
                'active_stores': len(active_stores),
                'online_stores': len(online_stores),
                'sync_health': f"{len(online_stores)}/{len(active_stores)} stores online"
            }
        })
    
    except Exception as e:
        logger.error(f"Error en health check multi-sede: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'service': 'multi-store-system',
            'error': str(e)
        }), 500
