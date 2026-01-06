"""
Health API v1 - Sistema POS O'Data
=================================
Endpoints de salud del sistema enterprise.
"""

from flask import Blueprint, jsonify  # type: ignore
from app import db
from sqlalchemy import text  # type: ignore
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Crear blueprint
health_bp = Blueprint('health', __name__)

# Configurar rate limiting


@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check básico del sistema"""
    try:
        # Verificar conexión a base de datos
        db.session.execute(text('SELECT 1'))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return jsonify({
        "status": "healthy",
        "message": "Sistema POS O'Data Enterprise funcionando correctamente",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.2-enterprise"
    })

@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Health check detallado del sistema"""
    try:
        health_data = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.2-enterprise",
            "components": {}
        }
        
        # Verificar base de datos
        try:
            db.session.execute(text('SELECT 1'))
            health_data["components"]["database"] = {
                "status": "healthy",
                "message": "Database connection successful"
            }
        except Exception as e:
            health_data["components"]["database"] = {
                "status": "unhealthy",
                "message": f"Database error: {str(e)}"
            }
            health_data["status"] = "unhealthy"
        
        # Verificar tablas principales
        try:
            tables = ['users', 'products', 'sales', 'sale_items', 'inventory_movements']
            for table in tables:
                db.session.execute(text(f'SELECT COUNT(*) FROM {table}'))
            
            health_data["components"]["tables"] = {
                "status": "healthy",
                "message": "All required tables accessible"
            }
        except Exception as e:
            health_data["components"]["tables"] = {
                "status": "unhealthy",
                "message": f"Table access error: {str(e)}"
            }
            health_data["status"] = "unhealthy"
        
        # Verificar logs
        try:
            import os
            log_dir = 'logs'
            if os.path.exists(log_dir) and os.access(log_dir, os.W_OK):
                health_data["components"]["logging"] = {
                    "status": "healthy",
                    "message": "Logging system operational"
                }
            else:
                health_data["components"]["logging"] = {
                    "status": "warning",
                    "message": "Logging directory not accessible"
                }
        except Exception as e:
            health_data["components"]["logging"] = {
                "status": "unhealthy",
                "message": f"Logging error: {str(e)}"
            }
        
        # Determinar status general
        component_statuses = [comp["status"] for comp in health_data["components"].values()]
        if "unhealthy" in component_statuses:
            health_data["status"] = "unhealthy"
        elif "warning" in component_statuses:
            health_data["status"] = "degraded"
        
        return jsonify(health_data)
        
    except Exception as e:
        logger.error(f"Error in detailed health check: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "message": "Health check failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }), 500

@health_bp.route('/health/metrics', methods=['GET'])
def health_metrics():
    """Métricas de salud del sistema"""
    try:
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {}
        }
        
        # Métricas de base de datos
        try:
            # Contar registros en tablas principales
            tables = ['users', 'products', 'sales', 'sale_items', 'inventory_movements']
            for table in tables:
                result = db.session.execute(text(f'SELECT COUNT(*) FROM {table}'))
                count = result.scalar()
                metrics["metrics"][f"{table}_count"] = count
        except Exception as e:
            metrics["metrics"]["database_error"] = str(e)
        
        # Métricas de ventas del día
        try:
            today = datetime.utcnow().date()
            result = db.session.execute(text("""
                SELECT 
                    COUNT(*) as sales_count,
                    COALESCE(SUM(total_amount), 0) as total_amount
                FROM sales 
                WHERE DATE(created_at) = :today
            """), {"today": today})
            
            row = result.fetchone()
            metrics["metrics"]["today_sales"] = {
                "count": row[0] if row else 0,
                "total_amount": float(row[1]) if row and row[1] else 0
            }
        except Exception as e:
            metrics["metrics"]["sales_error"] = str(e)
        
        return jsonify(metrics)
        
    except Exception as e:
        logger.error(f"Error in health metrics: {str(e)}")
        return jsonify({
            "error": "Failed to retrieve metrics",
            "message": str(e)
        }), 500
