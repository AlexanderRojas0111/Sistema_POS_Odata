"""
API de Reportes Profesional - Sistema POS Sabrositas
====================================================
Implementación robusta y enterprise-ready para reportes
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, and_, desc, text
from sqlalchemy.orm import joinedload
import logging
import csv
import io
from typing import Dict, Any, List, Optional

from app import db
from app.models.sale import Sale, SaleItem
from app.models.product import Product
from app.models.user import User

logger = logging.getLogger(__name__)

# Blueprint con nombre único
reports_professional_bp = Blueprint('reports_professional', __name__, url_prefix='/reports')

# ===============================================
# ENDPOINTS SIN AUTENTICACIÓN (PARA TESTING)
# ===============================================

@reports_professional_bp.route('/test/health', methods=['GET'])
def test_health():
    """Verificar salud del módulo de reportes"""
    try:
        # Test de conexión a BD simple
        result = db.session.execute(text('SELECT 1 as test')).fetchone()
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'message': 'Módulo de reportes funcionando correctamente',
            'database_test': result[0] if result else None,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Error en test_health: {str(e)}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@reports_professional_bp.route('/test/sales', methods=['GET'])
def test_sales_basic():
    """Reporte básico de ventas sin autenticación"""
    try:
        # Parámetros opcionales
        days = int(request.args.get('days', 30))
        start_date = datetime.now() - timedelta(days=days)
        
        # Consulta básica de ventas
        sales_count = db.session.query(func.count(Sale.id)).filter(
            Sale.created_at >= start_date
        ).scalar() or 0
        
        sales_total = db.session.query(func.coalesce(func.sum(Sale.total_amount), 0)).filter(
            Sale.created_at >= start_date
        ).scalar() or 0
        
        # Ventas por método de pago
        payment_stats = db.session.query(
            Sale.payment_method,
            func.count(Sale.id).label('count'),
            func.sum(Sale.total_amount).label('total')
        ).filter(
            Sale.created_at >= start_date
        ).group_by(Sale.payment_method).all()
        
        payment_methods = {}
        for stat in payment_stats:
            method = stat.payment_method or 'Efectivo'
            payment_methods[method] = {
                'count': stat.count,
                'total': float(stat.total or 0)
            }
        
        response_data = {
            'success': True,
            'data': {
                'period_days': days,
                'summary': {
                    'total_sales': sales_count,
                    'total_revenue': float(sales_total),
                    'average_sale': float(sales_total / sales_count) if sales_count > 0 else 0
                },
                'payment_methods': payment_methods
            },
            'message': f'Reporte de ventas de últimos {days} días generado exitosamente'
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error en test_sales_basic: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error generando reporte de ventas',
            'details': str(e)
        }), 500

@reports_professional_bp.route('/test/inventory', methods=['GET'])
def test_inventory_basic():
    """Reporte básico de inventario sin autenticación"""
    try:
        # Estadísticas de productos
        total_products = db.session.query(func.count(Product.id)).filter(
            Product.is_active == True
        ).scalar() or 0
        
        low_stock_products = db.session.query(func.count(Product.id)).filter(
            and_(
                Product.is_active == True,
                Product.stock <= func.coalesce(Product.min_stock, 5)
            )
        ).scalar() or 0
        
        out_of_stock_products = db.session.query(func.count(Product.id)).filter(
            and_(
                Product.is_active == True,
                Product.stock <= 0
            )
        ).scalar() or 0
        
        # Valor total del inventario
        inventory_value = db.session.query(
            func.coalesce(func.sum(Product.price * Product.stock), 0)
        ).filter(Product.is_active == True).scalar() or 0
        
        # Productos por categoría
        category_stats = db.session.query(
            Product.category,
            func.count(Product.id).label('count'),
            func.sum(Product.stock).label('total_stock')
        ).filter(
            Product.is_active == True
        ).group_by(Product.category).all()
        
        categories = {}
        for stat in category_stats:
            category = stat.category or 'Sin categoría'
            categories[category] = {
                'product_count': stat.count,
                'total_stock': stat.total_stock or 0
            }
        
        response_data = {
            'success': True,
            'data': {
                'summary': {
                    'total_products': total_products,
                    'low_stock_count': low_stock_products,
                    'out_of_stock_count': out_of_stock_products,
                    'inventory_value': float(inventory_value)
                },
                'categories': categories
            },
            'message': 'Reporte de inventario generado exitosamente'
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error en test_inventory_basic: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error generando reporte de inventario',
            'details': str(e)
        }), 500

@reports_professional_bp.route('/test/dashboard', methods=['GET'])
def test_dashboard_basic():
    """Dashboard básico sin autenticación"""
    try:
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        
        # Ventas de hoy
        today_sales = db.session.query(
            func.count(Sale.id),
            func.coalesce(func.sum(Sale.total_amount), 0)
        ).filter(
            func.date(Sale.created_at) == today
        ).first()
        
        # Ventas de ayer
        yesterday_sales = db.session.query(
            func.count(Sale.id),
            func.coalesce(func.sum(Sale.total_amount), 0)
        ).filter(
            func.date(Sale.created_at) == yesterday
        ).first()
        
        # Ventas de la semana
        week_sales = db.session.query(
            func.count(Sale.id),
            func.coalesce(func.sum(Sale.total_amount), 0)
        ).filter(
            Sale.created_at >= week_ago
        ).first()
        
        # Productos activos
        active_products = db.session.query(func.count(Product.id)).filter(
            Product.is_active == True
        ).scalar() or 0
        
        response_data = {
            'success': True,
            'data': {
                'sales_today': {
                    'count': today_sales[0] or 0,
                    'total': float(today_sales[1] or 0)
                },
                'sales_yesterday': {
                    'count': yesterday_sales[0] or 0,
                    'total': float(yesterday_sales[1] or 0)
                },
                'sales_week': {
                    'count': week_sales[0] or 0,
                    'total': float(week_sales[1] or 0)
                },
                'inventory': {
                    'active_products': active_products
                }
            },
            'message': 'Dashboard generado exitosamente'
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error en test_dashboard_basic: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error generando dashboard',
            'details': str(e)
        }), 500

# ===============================================
# ENDPOINTS CON AUTENTICACIÓN (PRODUCCIÓN)
# ===============================================

@reports_professional_bp.route('/sales', methods=['GET'])
def get_sales_report_public():
    """Reporte de ventas público (sin JWT por ahora)"""
    try:
        # Parámetros
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        format_type = request.args.get('format', 'json')
        
        # Fechas por defecto
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        # Consulta optimizada
        sales_data = db.session.query(
            Sale.id,
            Sale.created_at,
            Sale.total_amount,
            Sale.payment_method,
            User.username
        ).join(User, Sale.user_id == User.id).filter(
            and_(
                Sale.created_at >= start_dt,
                Sale.created_at < end_dt
            )
        ).order_by(desc(Sale.created_at)).all()
        
        # Procesar datos
        sales_list = []
        total_revenue = 0
        payment_methods = {}
        daily_sales = {}
        
        for sale in sales_data:
            sale_dict = {
                'id': sale.id,
                'date': sale.created_at.isoformat(),
                'total': float(sale.total_amount),
                'payment_method': sale.payment_method or 'Efectivo',
                'seller': sale.username
            }
            sales_list.append(sale_dict)
            
            # Acumular estadísticas
            total_revenue += float(sale.total_amount)
            
            # Por método de pago
            method = sale.payment_method or 'Efectivo'
            if method not in payment_methods:
                payment_methods[method] = {'count': 0, 'total': 0}
            payment_methods[method]['count'] += 1
            payment_methods[method]['total'] += float(sale.total_amount)
            
            # Por día
            day = sale.created_at.strftime('%Y-%m-%d')
            if day not in daily_sales:
                daily_sales[day] = {'count': 0, 'total': 0}
            daily_sales[day]['count'] += 1
            daily_sales[day]['total'] += float(sale.total_amount)
        
        response_data = {
            'success': True,
            'data': {
                'sales': sales_list,
                'summary': {
                    'total_sales': len(sales_list),
                    'total_revenue': total_revenue,
                    'average_sale': total_revenue / len(sales_list) if sales_list else 0,
                    'date_range': {'start': start_date, 'end': end_date}
                },
                'analytics': {
                    'payment_methods': payment_methods,
                    'daily_sales': daily_sales
                }
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error en get_sales_report_public: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error generando reporte de ventas',
            'details': str(e)
        }), 500

@reports_professional_bp.route('/inventory', methods=['GET'])
def get_inventory_report_public():
    """Reporte de inventario público"""
    try:
        # Consulta optimizada de productos
        products_data = db.session.query(Product).filter(
            Product.is_active == True
        ).order_by(Product.category, Product.name).all()
        
        # Procesar datos
        products_list = []
        categories = {}
        total_value = 0
        low_stock_count = 0
        out_of_stock_count = 0
        
        for product in products_data:
            # Estado del stock
            stock_status = 'normal'
            min_stock = product.min_stock or 5
            
            if product.stock <= 0:
                stock_status = 'out_of_stock'
                out_of_stock_count += 1
            elif product.stock <= min_stock:
                stock_status = 'low_stock'
                low_stock_count += 1
            
            product_dict = {
                'id': product.id,
                'name': product.name,
                'sku': product.sku or '',
                'category': product.category or 'Sin categoría',
                'price': float(product.price),
                'stock': product.stock,
                'min_stock': min_stock,
                'stock_value': float(product.price * product.stock),
                'stock_status': stock_status
            }
            products_list.append(product_dict)
            
            # Estadísticas por categoría
            category = product.category or 'Sin categoría'
            if category not in categories:
                categories[category] = {
                    'count': 0,
                    'total_stock': 0,
                    'total_value': 0
                }
            
            categories[category]['count'] += 1
            categories[category]['total_stock'] += product.stock
            categories[category]['total_value'] += float(product.price * product.stock)
            
            total_value += float(product.price * product.stock)
        
        response_data = {
            'success': True,
            'data': {
                'products': products_list,
                'summary': {
                    'total_products': len(products_list),
                    'low_stock_count': low_stock_count,
                    'out_of_stock_count': out_of_stock_count,
                    'total_inventory_value': total_value
                },
                'categories': categories
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error en get_inventory_report_public: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error generando reporte de inventario',
            'details': str(e)
        }), 500

@reports_professional_bp.route('/dashboard', methods=['GET'])
def get_dashboard_summary_public():
    """Dashboard público con métricas clave"""
    try:
        # Fechas de referencia
        now = datetime.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Métricas de ventas
        today_stats = db.session.query(
            func.count(Sale.id),
            func.coalesce(func.sum(Sale.total_amount), 0)
        ).filter(func.date(Sale.created_at) == today).first()
        
        yesterday_stats = db.session.query(
            func.count(Sale.id),
            func.coalesce(func.sum(Sale.total_amount), 0)
        ).filter(func.date(Sale.created_at) == yesterday).first()
        
        week_stats = db.session.query(
            func.count(Sale.id),
            func.coalesce(func.sum(Sale.total_amount), 0)
        ).filter(Sale.created_at >= week_ago).first()
        
        month_stats = db.session.query(
            func.count(Sale.id),
            func.coalesce(func.sum(Sale.total_amount), 0)
        ).filter(Sale.created_at >= month_ago).first()
        
        # Productos más vendidos (último mes)
        top_products_raw = db.session.query(
            Product.name,
            func.sum(SaleItem.quantity).label('total_sold'),
            func.sum(SaleItem.subtotal).label('revenue')
        ).select_from(Product).join(SaleItem).join(Sale).filter(
            Sale.created_at >= month_ago
        ).group_by(Product.id, Product.name).order_by(
            desc(func.sum(SaleItem.quantity))
        ).limit(5).all()
        
        top_products = [
            {
                'name': product[0],
                'quantity_sold': int(product[1] or 0),
                'revenue': float(product[2] or 0)
            } for product in top_products_raw
        ]
        
        # Métricas de inventario
        inventory_stats = db.session.query(
            func.count(Product.id),
            func.sum(Product.stock),
            func.sum(Product.price * Product.stock)
        ).filter(Product.is_active == True).first()
        
        low_stock_alerts = db.session.query(func.count(Product.id)).filter(
            and_(
                Product.is_active == True,
                Product.stock <= func.coalesce(Product.min_stock, 5)
            )
        ).scalar() or 0
        
        response_data = {
            'success': True,
            'data': {
                'sales_metrics': {
                    'today': {
                        'count': today_stats[0] or 0,
                        'total': float(today_stats[1] or 0)
                    },
                    'yesterday': {
                        'count': yesterday_stats[0] or 0,
                        'total': float(yesterday_stats[1] or 0)
                    },
                    'week': {
                        'count': week_stats[0] or 0,
                        'total': float(week_stats[1] or 0)
                    },
                    'month': {
                        'count': month_stats[0] or 0,
                        'total': float(month_stats[1] or 0)
                    }
                },
                'inventory_metrics': {
                    'total_products': inventory_stats[0] or 0,
                    'total_stock_units': inventory_stats[1] or 0,
                    'total_value': float(inventory_stats[2] or 0),
                    'low_stock_alerts': low_stock_alerts
                },
                'top_products': top_products
            },
            'message': 'Dashboard generado exitosamente'
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error en get_dashboard_summary_public: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error generando dashboard',
            'details': str(e)
        }), 500

@reports_professional_bp.route('/products/performance', methods=['GET'])
def get_product_performance_public():
    """Rendimiento de productos público"""
    try:
        days = int(request.args.get('days', 30))
        limit = int(request.args.get('limit', 20))
        
        start_date = datetime.now() - timedelta(days=days)
        
        # Productos más vendidos
        products_performance = db.session.query(
            Product.id,
            Product.name,
            Product.category,
            Product.price,
            Product.stock,
            func.coalesce(func.sum(SaleItem.quantity), 0).label('total_sold'),
            func.coalesce(func.sum(SaleItem.subtotal), 0).label('revenue'),
            func.count(Sale.id).label('sale_transactions')
        ).select_from(Product).outerjoin(SaleItem).outerjoin(Sale).filter(
            Sale.created_at >= start_date
        ).group_by(
            Product.id, Product.name, Product.category, Product.price, Product.stock
        ).order_by(
            desc(func.coalesce(func.sum(SaleItem.quantity), 0))
        ).limit(limit).all()
        
        products_list = []
        for product in products_performance:
            total_sold = int(product.total_sold or 0)
            revenue = float(product.revenue or 0)
            transactions = int(product.sale_transactions or 0)
            
            products_list.append({
                'id': product.id,
                'name': product.name,
                'category': product.category or 'Sin categoría',
                'price': float(product.price),
                'current_stock': product.stock,
                'quantity_sold': total_sold,
                'revenue': revenue,
                'transactions': transactions,
                'avg_per_transaction': total_sold / transactions if transactions > 0 else 0,
                'revenue_per_unit': revenue / total_sold if total_sold > 0 else 0
            })
        
        response_data = {
            'success': True,
            'data': {
                'products': products_list,
                'period_days': days,
                'total_products_analyzed': len(products_list)
            },
            'message': f'Análisis de rendimiento de productos (últimos {days} días)'
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error en get_product_performance_public: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error analizando rendimiento de productos',
            'details': str(e)
        }), 500

# ===============================================
# ENDPOINTS DE EXPORTACIÓN
# ===============================================

@reports_professional_bp.route('/export/sales/csv', methods=['GET'])
def export_sales_csv():
    """Exportar ventas a CSV"""
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        # Obtener ventas
        sales = db.session.query(
            Sale.id,
            Sale.created_at,
            Sale.total_amount,
            Sale.payment_method,
            User.username
        ).join(User).filter(
            and_(Sale.created_at >= start_dt, Sale.created_at < end_dt)
        ).order_by(Sale.created_at).all()
        
        # Generar CSV
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Fecha', 'Hora', 'Total', 'Método Pago', 'Vendedor'])
        
        for sale in sales:
            writer.writerow([
                sale.id,
                sale.created_at.strftime('%Y-%m-%d'),
                sale.created_at.strftime('%H:%M:%S'),
                sale.total_amount,
                sale.payment_method or 'Efectivo',
                sale.username
            ])
        
        csv_content = output.getvalue()
        output.close()
        
        return jsonify({
            'success': True,
            'data': {
                'csv_content': csv_content,
                'filename': f'ventas_{start_date}_to_{end_date}.csv',
                'records_count': len(sales)
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error exportando ventas CSV: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error exportando ventas',
            'details': str(e)
        }), 500

# ===============================================
# ERROR HANDLERS
# ===============================================

@reports_professional_bp.errorhandler(404)
def not_found_handler(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado',
        'message': 'El endpoint de reportes solicitado no existe'
    }), 404

@reports_professional_bp.errorhandler(500)
def internal_error_handler(error):
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor',
        'message': 'Ha ocurrido un error inesperado en el módulo de reportes'
    }), 500
