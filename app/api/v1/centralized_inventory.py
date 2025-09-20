"""
Centralized Inventory API v1 - Sistema Multi-Sede Sabrositas
===========================================================
APIs para gestión centralizada de inventario multi-tienda.
"""

from flask import Blueprint, request, jsonify
from app.services.centralized_inventory_service import CentralizedInventoryService
from app.services.auth_service import AuthService
from app.middleware.auth_middleware import require_auth, require_role
from app.exceptions import ValidationError, BusinessLogicError
import logging

logger = logging.getLogger(__name__)

# Blueprint para APIs de inventario centralizado
centralized_inventory_bp = Blueprint('centralized_inventory', __name__)

# Inicializar servicios
inventory_service = CentralizedInventoryService()
auth_service = AuthService()

@centralized_inventory_bp.route('/inventory/global-summary', methods=['GET'])
@require_auth
@require_role('manager')
def get_global_inventory_summary():
    """Obtener resumen global de inventario"""
    try:
        summary = inventory_service.get_global_inventory_summary()
        
        return jsonify({
            'status': 'success',
            'data': summary
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo resumen global de inventario: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo resumen global de inventario',
            'error': str(e)
        }), 500

@centralized_inventory_bp.route('/inventory/product/<int:product_id>/distribution', methods=['GET'])
@require_auth
def get_product_distribution(product_id):
    """Obtener distribución de un producto en todas las tiendas"""
    try:
        distribution = inventory_service.get_product_distribution(product_id)
        
        return jsonify({
            'status': 'success',
            'data': distribution
        })
    
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Error obteniendo distribución del producto {product_id}: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo distribución del producto',
            'error': str(e)
        }), 500

@centralized_inventory_bp.route('/inventory/rebalancing/suggestions', methods=['GET'])
@require_auth
@require_role('manager')
def get_rebalancing_suggestions():
    """Obtener sugerencias de rebalanceo de inventario"""
    try:
        suggestions = inventory_service.suggest_inventory_rebalancing()
        
        return jsonify({
            'status': 'success',
            'data': {
                'suggestions': suggestions,
                'total_suggestions': len(suggestions)
            },
            'message': f'Se encontraron {len(suggestions)} sugerencias de rebalanceo'
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo sugerencias de rebalanceo: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo sugerencias de rebalanceo',
            'error': str(e)
        }), 500

@centralized_inventory_bp.route('/inventory/rebalancing/auto-transfer', methods=['POST'])
@require_auth
@require_role('manager')
def create_automatic_transfer():
    """Crear transferencia automática basada en sugerencia"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos requeridos'
            }), 400
        
        suggestion = data.get('suggestion')
        if not suggestion:
            return jsonify({
                'status': 'error',
                'message': 'Sugerencia requerida'
            }), 400
        
        # Obtener usuario actual del token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_data = auth_service.decode_token(token)
        
        transfer = inventory_service.create_automatic_transfer(
            suggestion, 
            user_data['user_id']
        )
        
        if transfer:
            return jsonify({
                'status': 'success',
                'message': f'Transferencia automática creada: {transfer.transfer_number}',
                'data': {
                    'transfer': transfer.to_dict()
                }
            }), 201
        else:
            return jsonify({
                'status': 'error',
                'message': 'No se pudo crear la transferencia automática'
            }), 422
    
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Error creando transferencia automática: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error creando transferencia automática',
            'error': str(e)
        }), 500

@centralized_inventory_bp.route('/inventory/alerts', methods=['GET'])
@require_auth
def get_inventory_alerts():
    """Obtener alertas de inventario"""
    try:
        severity = request.args.get('severity')  # high, medium, low
        alerts = inventory_service.get_inventory_alerts(severity=severity)
        
        return jsonify({
            'status': 'success',
            'data': {
                'alerts': alerts,
                'total_alerts': len(alerts),
                'filter_severity': severity
            }
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo alertas de inventario: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo alertas de inventario',
            'error': str(e)
        }), 500

@centralized_inventory_bp.route('/inventory/reconciliation', methods=['POST'])
@require_auth
@require_role('manager')
def execute_inventory_reconciliation():
    """Ejecutar reconciliación de inventario"""
    try:
        data = request.get_json() or {}
        store_id = data.get('store_id')  # Opcional: reconciliar solo una tienda
        
        results = inventory_service.execute_inventory_reconciliation(store_id=store_id)
        
        return jsonify({
            'status': 'success',
            'message': 'Reconciliación de inventario completada',
            'data': results
        })
    
    except ValidationError as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Error ejecutando reconciliación de inventario: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error ejecutando reconciliación de inventario',
            'error': str(e)
        }), 500

@centralized_inventory_bp.route('/inventory/trends', methods=['GET'])
@require_auth
@require_role('manager')
def get_inventory_trends():
    """Obtener tendencias de inventario"""
    try:
        days = request.args.get('days', default=30, type=int)
        
        if days < 1 or days > 365:
            return jsonify({
                'status': 'error',
                'message': 'El parámetro days debe estar entre 1 y 365'
            }), 400
        
        trends = inventory_service.get_inventory_trends(days=days)
        
        return jsonify({
            'status': 'success',
            'data': trends
        })
    
    except Exception as e:
        logger.error(f"Error obteniendo tendencias de inventario: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error obteniendo tendencias de inventario',
            'error': str(e)
        }), 500

@centralized_inventory_bp.route('/inventory/health-check', methods=['GET'])
@require_auth
def inventory_health_check():
    """Health check del sistema de inventario centralizado"""
    try:
        # Obtener métricas básicas de salud
        summary = inventory_service.get_global_inventory_summary()
        alerts = inventory_service.get_inventory_alerts(severity='high')
        
        health_score = summary['summary']['inventory_health_score']
        critical_alerts = len(alerts)
        
        # Determinar estado de salud
        if health_score >= 90 and critical_alerts == 0:
            status = 'healthy'
        elif health_score >= 70 and critical_alerts <= 5:
            status = 'warning'
        else:
            status = 'critical'
        
        return jsonify({
            'service': 'centralized-inventory',
            'status': status,
            'health_score': health_score,
            'metrics': {
                'total_stores': summary['summary']['active_stores'],
                'total_products': summary['summary']['total_products'],
                'critical_stock_products': summary['summary']['critical_stock_products'],
                'out_of_stock_products': summary['summary']['out_of_stock_products'],
                'active_transfers': summary['summary']['active_transfers'],
                'critical_alerts': critical_alerts,
                'total_inventory_value': summary['summary']['total_inventory_value']
            },
            'timestamp': summary['timestamp']
        })
    
    except Exception as e:
        logger.error(f"Error en health check de inventario centralizado: {str(e)}")
        return jsonify({
            'service': 'centralized-inventory',
            'status': 'unhealthy',
            'error': str(e)
        }), 503

@centralized_inventory_bp.route('/inventory/batch-operations', methods=['POST'])
@require_auth
@require_role('manager')
def execute_batch_operations():
    """Ejecutar operaciones en lote sobre inventario"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'status': 'error',
                'message': 'Datos requeridos'
            }), 400
        
        operation_type = data.get('operation_type')
        operations = data.get('operations', [])
        
        if not operation_type or not operations:
            return jsonify({
                'status': 'error',
                'message': 'operation_type y operations requeridos'
            }), 400
        
        results = {
            'operation_type': operation_type,
            'total_operations': len(operations),
            'successful_operations': 0,
            'failed_operations': 0,
            'results': []
        }
        
        # Obtener usuario actual
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_data = auth_service.decode_token(token)
        
        # Procesar operaciones según el tipo
        if operation_type == 'bulk_rebalancing':
            # Crear múltiples transferencias automáticas
            for operation in operations:
                try:
                    suggestion = operation.get('suggestion')
                    if suggestion:
                        transfer = inventory_service.create_automatic_transfer(
                            suggestion, 
                            user_data['user_id']
                        )
                        if transfer:
                            results['successful_operations'] += 1
                            results['results'].append({
                                'operation': operation,
                                'success': True,
                                'transfer_number': transfer.transfer_number
                            })
                        else:
                            results['failed_operations'] += 1
                            results['results'].append({
                                'operation': operation,
                                'success': False,
                                'error': 'No se pudo crear la transferencia'
                            })
                except Exception as e:
                    results['failed_operations'] += 1
                    results['results'].append({
                        'operation': operation,
                        'success': False,
                        'error': str(e)
                    })
        
        elif operation_type == 'bulk_reconciliation':
            # Reconciliar múltiples tiendas
            for operation in operations:
                try:
                    store_id = operation.get('store_id')
                    if store_id:
                        reconciliation_result = inventory_service.execute_inventory_reconciliation(
                            store_id=store_id
                        )
                        results['successful_operations'] += 1
                        results['results'].append({
                            'operation': operation,
                            'success': True,
                            'reconciliation_result': reconciliation_result
                        })
                except Exception as e:
                    results['failed_operations'] += 1
                    results['results'].append({
                        'operation': operation,
                        'success': False,
                        'error': str(e)
                    })
        
        else:
            return jsonify({
                'status': 'error',
                'message': f'Tipo de operación no soportado: {operation_type}'
            }), 400
        
        return jsonify({
            'status': 'success',
            'message': f'Operaciones en lote completadas: {results["successful_operations"]}/{results["total_operations"]} exitosas',
            'data': results
        })
    
    except Exception as e:
        logger.error(f"Error ejecutando operaciones en lote: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Error ejecutando operaciones en lote',
            'error': str(e)
        }), 500

# Endpoint para métricas de Prometheus
@centralized_inventory_bp.route('/inventory/metrics', methods=['GET'])
def inventory_metrics():
    """Métricas de inventario para Prometheus"""
    try:
        summary = inventory_service.get_global_inventory_summary()
        alerts = inventory_service.get_inventory_alerts()
        
        # Formato de métricas para Prometheus
        metrics_lines = []
        
        # Métricas básicas
        metrics_lines.append(f'inventory_total_products {summary["summary"]["total_products"]}')
        metrics_lines.append(f'inventory_active_stores {summary["summary"]["active_stores"]}')
        metrics_lines.append(f'inventory_total_value {summary["summary"]["total_inventory_value"]}')
        metrics_lines.append(f'inventory_critical_stock_products {summary["summary"]["critical_stock_products"]}')
        metrics_lines.append(f'inventory_out_of_stock_products {summary["summary"]["out_of_stock_products"]}')
        metrics_lines.append(f'inventory_active_transfers {summary["summary"]["active_transfers"]}')
        metrics_lines.append(f'inventory_health_score {summary["summary"]["inventory_health_score"]}')
        
        # Métricas de alertas por severidad
        high_alerts = len([a for a in alerts if a['severity'] == 'high'])
        medium_alerts = len([a for a in alerts if a['severity'] == 'medium'])
        low_alerts = len([a for a in alerts if a['severity'] == 'low'])
        
        metrics_lines.append(f'inventory_alerts_high {high_alerts}')
        metrics_lines.append(f'inventory_alerts_medium {medium_alerts}')
        metrics_lines.append(f'inventory_alerts_low {low_alerts}')
        
        return '\n'.join(metrics_lines), 200, {'Content-Type': 'text/plain'}
    
    except Exception as e:
        logger.error(f"Error generando métricas de inventario: {str(e)}")
        return f'inventory_metrics_error 1\n', 500, {'Content-Type': 'text/plain'}
