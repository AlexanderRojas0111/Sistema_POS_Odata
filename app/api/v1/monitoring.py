"""
Endpoints de Monitoreo - Sistema POS O'Data
==========================================
Endpoints para métricas, salud y monitoreo del sistema
"""

from flask import Blueprint, jsonify, request
from app.monitoring.metrics import metrics_collector, health_checker
from app.monitoring.alerts import get_alert_stats, get_recent_alerts
from app.middleware.error_handler_enhanced import error_handler, APIError
import logging

logger = logging.getLogger(__name__)

monitoring_bp = Blueprint('monitoring', __name__)

@monitoring_bp.route('/health', methods=['GET'])
@error_handler
def health_check():
    """
    Endpoint de verificación de salud del sistema
    """
    health_status = health_checker.run_health_checks()
    
    status_code = 200 if health_status['overall_status'] == 'healthy' else 503
    
    return jsonify({
        "success": True,
        "data": health_status
    }), status_code

@monitoring_bp.route('/health/detailed', methods=['GET'])
@error_handler
def detailed_health_check():
    """
    Endpoint de verificación de salud detallada
    """
    health_status = health_checker.run_health_checks()
    metrics = metrics_collector.get_metrics()
    
    # Información adicional del sistema
    system_info = {
        "python_version": __import__('sys').version,
        "flask_version": __import__('flask').__version__,
        "environment": request.environ.get('FLASK_ENV', 'production'),
        "host": request.host,
        "user_agent": request.headers.get('User-Agent', 'Unknown')
    }
    
    detailed_status = {
        "health": health_status,
        "metrics": metrics,
        "system": system_info
    }
    
    status_code = 200 if health_status['overall_status'] == 'healthy' else 503
    
    return jsonify({
        "success": True,
        "data": detailed_status
    }), status_code

@monitoring_bp.route('/metrics', methods=['GET'])
@error_handler
def get_metrics():
    """
    Endpoint para obtener métricas del sistema
    """
    metrics = metrics_collector.get_metrics()
    
    return jsonify({
        "success": True,
        "data": metrics
    })

@monitoring_bp.route('/metrics/summary', methods=['GET'])
@error_handler
def get_metrics_summary():
    """
    Endpoint para obtener resumen de métricas
    """
    metrics = metrics_collector.get_metrics()
    
    # Crear resumen
    summary = {
        "uptime": metrics["uptime_human"],
        "total_requests": metrics["total_requests"],
        "requests_per_minute": metrics["requests_per_minute"],
        "average_response_time_ms": metrics["average_response_time_ms"],
        "active_requests": metrics["active_requests"],
        "total_errors": sum(metrics["error_counts"].values()),
        "status": "healthy" if metrics["average_response_time_ms"] < 1000 else "degraded"
    }
    
    return jsonify({
        "success": True,
        "data": summary
    })

@monitoring_bp.route('/metrics/errors', methods=['GET'])
@error_handler
def get_error_metrics():
    """
    Endpoint para obtener métricas de errores
    """
    metrics = metrics_collector.get_metrics()
    
    error_summary = {
        "total_errors": sum(metrics["error_counts"].values()),
        "error_breakdown": metrics["error_counts"],
        "error_rate": 0
    }
    
    # Calcular tasa de errores
    total_requests = metrics["total_requests"]
    if total_requests > 0:
        error_summary["error_rate"] = round(
            (error_summary["total_errors"] / total_requests) * 100, 2
        )
    
    return jsonify({
        "success": True,
        "data": error_summary
    })

@monitoring_bp.route('/metrics/performance', methods=['GET'])
@error_handler
def get_performance_metrics():
    """
    Endpoint para obtener métricas de rendimiento
    """
    metrics = metrics_collector.get_metrics()
    
    performance_summary = {
        "average_response_time_ms": metrics["average_response_time_ms"],
        "requests_per_minute": metrics["requests_per_minute"],
        "active_requests": metrics["active_requests"],
        "uptime_seconds": metrics["uptime_seconds"],
        "performance_status": "excellent" if metrics["average_response_time_ms"] < 100 else
                           "good" if metrics["average_response_time_ms"] < 500 else
                           "fair" if metrics["average_response_time_ms"] < 1000 else
                           "poor"
    }
    
    return jsonify({
        "success": True,
        "data": performance_summary
    })

@monitoring_bp.route('/status', methods=['GET'])
@error_handler
def system_status():
    """
    Endpoint de estado del sistema (compatible con load balancers)
    """
    health_status = health_checker.run_health_checks()
    
    if health_status['overall_status'] == 'healthy':
        return jsonify({
            "status": "ok",
            "message": "Sistema funcionando correctamente"
        }), 200
    else:
        return jsonify({
            "status": "error",
            "message": "Sistema con problemas",
            "details": health_status
        }), 503

@monitoring_bp.route('/ping', methods=['GET'])
@error_handler
def ping():
    """
    Endpoint de ping simple
    """
    return jsonify({
        "pong": True,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    })

@monitoring_bp.route('/version', methods=['GET'])
@error_handler
def version_info():
    """
    Endpoint de información de versión
    """
    version_info = {
        "application": "Sistema POS O'Data",
        "version": "2.0.0-enterprise",
        "python_version": __import__('sys').version,
        "flask_version": __import__('flask').__version__,
        "environment": request.environ.get('FLASK_ENV', 'production'),
        "build_date": "2025-09-24",
        "api_version": "v1"
    }
    
    return jsonify({
        "success": True,
        "data": version_info
    })

@monitoring_bp.route('/metrics/reset', methods=['POST'])
@error_handler
def reset_metrics():
    """
    Endpoint para resetear métricas (solo en desarrollo)
    """
    if request.environ.get('FLASK_ENV') != 'development':
        raise APIError("Esta operación solo está disponible en desarrollo", 403)
    
    # Resetear métricas
    metrics_collector._metrics.clear()
    metrics_collector._response_times.clear()
    metrics_collector._error_counts.clear()
    metrics_collector._active_requests = 0
    
    logger.info("Métricas reseteadas por administrador")
    
    return jsonify({
        "success": True,
        "message": "Métricas reseteadas correctamente"
    })

@monitoring_bp.route('/redis/info', methods=['GET'])
@error_handler
def get_redis_info():
    """
    Endpoint para obtener información de Redis
    """
    try:
        from app.config.redis_config import get_redis_info
        redis_info = get_redis_info()
        
        return jsonify({
            "success": True,
            "data": redis_info
        })
        
    except Exception as e:
        logger.error(f"Error getting Redis info: {e}")
        raise APIError("Error al obtener información de Redis", 500)

@monitoring_bp.route('/rate-limit/info', methods=['GET'])
@error_handler
def get_rate_limit_info():
    """
    Endpoint para obtener información de rate limiting
    """
    try:
        from app.security.rate_limiter_enhanced import rate_limiter
        
        # Obtener información para el endpoint actual
        info = rate_limiter.get_rate_limit_info()
        
        return jsonify({
            "success": True,
            "data": {
                "current_endpoint": info,
                "client_ip": request.remote_addr,
                "user_agent": request.headers.get('User-Agent', 'Unknown')
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting rate limit info: {e}")
        raise APIError("Error al obtener información de rate limiting", 500)

@monitoring_bp.route('/logs/recent', methods=['GET'])
@error_handler
def get_recent_logs():
    """
    Endpoint para obtener logs recientes (solo en desarrollo)
    """
    if request.environ.get('FLASK_ENV') != 'development':
        raise APIError("Esta operación solo está disponible en desarrollo", 403)
    
    try:
        import os
        log_file = 'logs/app.log'
        
        if not os.path.exists(log_file):
            return jsonify({
                "success": True,
                "data": {
                    "logs": [],
                    "message": "Archivo de log no encontrado"
                }
            })
        
        # Leer últimas 50 líneas
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            recent_logs = lines[-50:] if len(lines) > 50 else lines
        
        return jsonify({
            "success": True,
            "data": {
                "logs": [line.strip() for line in recent_logs],
                "total_lines": len(lines)
            }
        })
        
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        raise APIError("Error al leer logs", 500)

@monitoring_bp.route('/alerts', methods=['GET'])
@error_handler
def get_alerts():
    """
    Endpoint para obtener alertas recientes
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        alerts = get_recent_alerts(limit)
        
        # Convertir alertas a formato serializable
        alerts_data = []
        for alert in alerts:
            alert_dict = {
                'id': alert.id,
                'type': alert.type.value,
                'level': alert.level.value,
                'title': alert.title,
                'message': alert.message,
                'timestamp': alert.timestamp.isoformat(),
                'source': alert.source,
                'metadata': alert.metadata,
                'resolved': alert.resolved,
                'resolved_at': alert.resolved_at.isoformat() if alert.resolved_at else None
            }
            alerts_data.append(alert_dict)
        
        return jsonify({
            "success": True,
            "data": {
                "alerts": alerts_data,
                "total": len(alerts_data)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting alerts: {e}")
        raise APIError("Error al obtener alertas", 500)

@monitoring_bp.route('/alerts/stats', methods=['GET'])
@error_handler
def get_alerts_stats():
    """
    Endpoint para obtener estadísticas de alertas
    """
    try:
        stats = get_alert_stats()
        
        return jsonify({
            "success": True,
            "data": stats
        })
        
    except Exception as e:
        logger.error(f"Error getting alert stats: {e}")
        raise APIError("Error al obtener estadísticas de alertas", 500)
