"""
Sync API v1 - Sistema de Sincronización Multi-Sede
==================================================
APIs para sincronización de datos entre tiendas Sabrositas.
"""

from flask import Blueprint, request, jsonify, current_app
from app.services.sync_service import SyncService
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import require_auth, require_role
from app.exceptions import ValidationError, SyncError
import logging

logger = logging.getLogger(__name__)

# Blueprint para APIs de sincronización
sync_bp = Blueprint('sync', __name__)

# Inicializar servicios
sync_service = SyncService()
auth_service = AuthService()

@sync_bp.route('/sync/status', methods=['GET'])
@require_auth
def get_sync_status():
    """Obtener estado de sincronización global o de una tienda"""
    try:
        store_id = request.args.get('store_id', type=int)
        status = sync_service.get_sync_status(store_id=store_id)
        
        return jsonify({
            'status': 'success',
            'data': status
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo estado de sincronización: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo estado de sincronización',
            'error': str(e)
        }), 500

@sync_bp.route('/sync/stores', methods=['POST'])
@require_auth
@require_role('manager')
def sync_all_stores():
    """Sincronizar todas las tiendas activas"""
    try:
        results = sync_service.sync_all_stores()
        
        return jsonify({
            'status': 'success',
            'message': 'Sincronización masiva completada',
            'data': results
        })
    
    except Exception as e:
        logger.error(f"Error en sincronización masiva: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error en sincronización masiva',
            'error': str(e)
        }), 500

@sync_bp.route('/sync/stores/<int:store_id>', methods=['POST'])
@require_auth
def sync_store(store_id):
    """Sincronizar una tienda específica"""
    try:
        result = sync_service.sync_store(store_id)
        
        if result['success']:
            return jsonify({
                'status': 'success',
                'message': f'Tienda {store_id} sincronizada exitosamente',
                'data': result
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Error sincronizando tienda {store_id}',
                'data': result
            }), 422
    
    except Exception as e:
        logger.error(f"Error sincronizando tienda {store_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'Error sincronizando tienda {store_id}',
            'error': str(e)
        }), 500

@sync_bp.route('/sync/queue/product', methods=['POST'])
@require_auth
def queue_product_sync():
    """Encolar sincronización de producto"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos requeridos'
            }), 400
        
        store_id = data.get('store_id')
        product_data = data.get('product_data', {})
        
        if not store_id:
            return jsonify({
                'status': 'error',
                'message': 'store_id requerido'
            }), 400
        
        success = sync_service.queue_sync_operation('product_update', store_id, product_data)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Sincronización de producto encolada',
                'data': {
                    'store_id': store_id,
                    'operation': 'product_update'
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error encolando sincronización de producto'
            }), 500
    
    except Exception as e:
        logger.error(f"Error encolando sincronización de producto: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error encolando sincronización de producto',
            'error': str(e)
        }), 500

@sync_bp.route('/sync/queue/inventory', methods=['POST'])
@require_auth
def queue_inventory_sync():
    """Encolar sincronización de inventario"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos requeridos'
            }), 400
        
        store_id = data.get('store_id')
        inventory_data = data.get('inventory_data', {})
        
        if not store_id:
            return jsonify({
                'status': 'error',
                'message': 'store_id requerido'
            }), 400
        
        success = sync_service.queue_sync_operation('inventory_adjustment', store_id, inventory_data)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Sincronización de inventario encolada',
                'data': {
                    'store_id': store_id,
                    'operation': 'inventory_adjustment'
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error encolando sincronización de inventario'
            }), 500
    
    except Exception as e:
        logger.error(f"Error encolando sincronización de inventario: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error encolando sincronización de inventario',
            'error': str(e)
        }), 500

@sync_bp.route('/sync/queue/price', methods=['POST'])
@require_auth
@require_role('manager')
def queue_price_sync():
    """Encolar sincronización de precios"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos requeridos'
            }), 400
        
        store_id = data.get('store_id')
        price_data = data.get('price_data', {})
        
        if not store_id:
            return jsonify({
                'status': 'error',
                'message': 'store_id requerido'
            }), 400
        
        success = sync_service.queue_sync_operation('price_update', store_id, price_data)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Sincronización de precios encolada',
                'data': {
                    'store_id': store_id,
                    'operation': 'price_update'
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error encolando sincronización de precios'
            }), 500
    
    except Exception as e:
        logger.error(f"Error encolando sincronización de precios: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error encolando sincronización de precios',
            'error': str(e)
        }), 500

@sync_bp.route('/sync/queue/transfer', methods=['POST'])
@require_auth
def queue_transfer_sync():
    """Encolar notificación de transferencia"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos requeridos'
            }), 400
        
        store_id = data.get('store_id')
        transfer_data = data.get('transfer_data', {})
        
        if not store_id:
            return jsonify({
                'status': 'error',
                'message': 'store_id requerido'
            }), 400
        
        success = sync_service.queue_sync_operation('transfer_notification', store_id, transfer_data)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Notificación de transferencia encolada',
                'data': {
                    'store_id': store_id,
                    'operation': 'transfer_notification'
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error encolando notificación de transferencia'
            }), 500
    
    except Exception as e:
        logger.error(f"Error encolando notificación de transferencia: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error encolando notificación de transferencia',
            'error': str(e)
        }), 500

@sync_bp.route('/sync/health', methods=['GET'])
def sync_health():
    """Health check del sistema de sincronización"""
    try:
        # Verificar estado de Redis
        redis_status = 'healthy'
        try:
            if sync_service.redis_client:
                sync_service.redis_client.ping()
            else:
                redis_status = 'not_configured'
        except Exception:
            redis_status = 'unhealthy'
        
        # Obtener estado general de sincronización
        sync_status = sync_service.get_sync_status()
        
        health_data = {
            'service': 'sync-service',
            'status': 'healthy' if redis_status != 'unhealthy' else 'degraded',
            'components': {
                'redis': redis_status,
                'sync_worker': 'running',  # Simplificado por ahora
                'database': 'healthy'
            },
            'metrics': {
                'total_stores': sync_status.get('total_stores', 0),
                'online_stores': sync_status.get('online_stores', 0),
                'sync_health_percentage': sync_status.get('sync_health_percentage', 0)
            }
        }
        
        status_code = 200 if health_data['status'] == 'healthy' else 503
        
        return jsonify(health_data), status_code
    
    except Exception as e:
        logger.error(f"Error en health check de sincronización: {str(e)}")
        return jsonify({
            'service': 'sync-service',
            'status': 'unhealthy',
            'error': str(e)
        }), 503

@sync_bp.route('/sync/metrics', methods=['GET'])
@require_auth
@require_role('manager')
def get_sync_metrics():
    """Obtener métricas detalladas de sincronización"""
    try:
        # Obtener métricas de Redis si está disponible
        redis_metrics = {}
        if sync_service.redis_client:
            try:
                info = sync_service.redis_client.info()
                redis_metrics = {
                    'connected_clients': info.get('connected_clients', 0),
                    'used_memory_human': info.get('used_memory_human', '0B'),
                    'total_commands_processed': info.get('total_commands_processed', 0),
                    'keyspace_hits': info.get('keyspace_hits', 0),
                    'keyspace_misses': info.get('keyspace_misses', 0)
                }
            except Exception as e:
                redis_metrics = {'error': str(e)}
        
        # Obtener estado de sincronización
        sync_status = sync_service.get_sync_status()
        
        metrics = {
            'sync_status': sync_status,
            'redis_metrics': redis_metrics,
            'timestamp': sync_service.sync_status.get('last_update', 'never')
        }
        
        return jsonify({
            'status': 'success',
            'data': metrics
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo métricas de sincronización: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo métricas de sincronización',
            'error': str(e)
        }), 500

# Webhook para notificaciones de sincronización (para integraciones externas)
@sync_bp.route('/sync/webhook', methods=['POST'])
def sync_webhook():
    """Webhook para recibir notificaciones de sincronización"""
    try:
        # Verificar autenticación del webhook
        webhook_secret = request.headers.get('X-Webhook-Secret')
        expected_secret = current_app.config.get('WEBHOOK_SECRET')
        
        if webhook_secret != expected_secret:
            return jsonify({
                'status': 'error',
                'message': 'Webhook no autorizado'
            }), 401
        
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos requeridos'
            }), 400
        
        event_type = data.get('event_type')
        store_id = data.get('store_id')
        payload = data.get('payload', {})
        
        if not event_type or not store_id:
            return jsonify({
                'status': 'error',
                'message': 'event_type y store_id requeridos'
            }), 400
        
        # Procesar evento de webhook
        success = sync_service.queue_sync_operation(event_type, store_id, payload)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Evento de webhook procesado',
                'data': {
                    'event_type': event_type,
                    'store_id': store_id
                }
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Error procesando evento de webhook'
            }), 500
    
    except Exception as e:
        logger.error(f"Error procesando webhook de sincronización: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error procesando webhook',
            'error': str(e)
        }), 500
