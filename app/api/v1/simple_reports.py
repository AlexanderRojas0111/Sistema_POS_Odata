"""
API de Reportes Simplificada - Sistema POS Sabrositas
Endpoints para generar reportes de ventas, inventario y analytics
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from sqlalchemy import func, and_, desc, text
import logging
import csv
import io
from typing import Dict, Any, List

from app import db
from app.models.sale import Sale, SaleItem
from app.models.product import Product
from app.models.user import User
from app.middleware.rbac_middleware import require_permission

logger = logging.getLogger(__name__)

simple_reports_bp = Blueprint('simple_reports', __name__, url_prefix='/reports')

@simple_reports_bp.route('/sales', methods=['GET'])
@jwt_required()
@require_permission('report_view')
def get_sales_report():
    """Generar reporte de ventas"""
    try:
        # Parámetros de consulta
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        format_type = request.args.get('format', 'json')
        
        # Fechas por defecto (último mes)
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
            
        # Convertir a datetime
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
        
        # Consulta de ventas
        sales_query = db.session.query(
            Sale.id,
            Sale.created_at,
            Sale.total_amount,
            Sale.payment_method,
            User.username.label('seller_name')
        ).join(User, Sale.user_id == User.id).filter(
            and_(
                Sale.created_at >= start_dt,
                Sale.created_at < end_dt
            )
        ).order_by(desc(Sale.created_at))
        
        sales = sales_query.all()
        
        # Estadísticas
        total_sales = len(sales)
        total_revenue = sum(sale.total_amount for sale in sales)
        avg_sale = total_revenue / total_sales if total_sales > 0 else 0
        
        # Ventas por método de pago
        payment_methods = {}
        for sale in sales:
            method = sale.payment_method or 'Efectivo'
            if method not in payment_methods:
                payment_methods[method] = {'count': 0, 'total': 0}
            payment_methods[method]['count'] += 1
            payment_methods[method]['total'] += float(sale.total_amount)
        
        # Ventas por día
        daily_sales = {}
        for sale in sales:
            day = sale.created_at.strftime('%Y-%m-%d')
            if day not in daily_sales:
                daily_sales[day] = {'count': 0, 'total': 0}
            daily_sales[day]['count'] += 1
            daily_sales[day]['total'] += float(sale.total_amount)
        
        # Formatear respuesta
        sales_data = []
        for sale in sales:
            sales_data.append({
                'id': sale.id,
                'date': sale.created_at.isoformat(),
                'total': float(sale.total_amount),
                'payment_method': sale.payment_method,
                'seller': sale.seller_name
            })
        
        response_data = {
            'success': True,
            'data': {
                'sales': sales_data,
                'summary': {
                    'total_sales': total_sales,
                    'total_revenue': float(total_revenue),
                    'average_sale': float(avg_sale),
                    'date_range': {
                        'start': start_date,
                        'end': end_date
                    }
                },
                'analytics': {
                    'payment_methods': payment_methods,
                    'daily_sales': daily_sales
                }
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error generando reporte de ventas: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@simple_reports_bp.route('/inventory', methods=['GET'])
@jwt_required()
@require_permission('report_view')
def get_inventory_report():
    """Generar reporte de inventario"""
    try:
        format_type = request.args.get('format', 'json')
        
        # Consulta de productos con stock
        products_query = db.session.query(Product).filter(
            Product.is_active == True
        ).order_by(Product.category, Product.name)
        
        products = products_query.all()
        
        # Estadísticas
        total_products = len(products)
        low_stock_products = [p for p in products if p.stock <= (p.min_stock or 5)]
        out_of_stock_products = [p for p in products if p.stock <= 0]
        
        # Productos por categoría
        categories = {}
        total_value = 0
        
        for product in products:
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
        
        # Formatear productos
        products_data = []
        for product in products:
            stock_status = 'normal'
            if product.stock <= 0:
                stock_status = 'out_of_stock'
            elif product.stock <= (product.min_stock or 5):
                stock_status = 'low_stock'
                
            products_data.append({
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'category': product.category,
                'price': float(product.price),
                'stock': product.stock,
                'min_stock': product.min_stock or 5,
                'stock_value': float(product.price * product.stock),
                'stock_status': stock_status
            })
        
        response_data = {
            'success': True,
            'data': {
                'products': products_data,
                'summary': {
                    'total_products': total_products,
                    'low_stock_count': len(low_stock_products),
                    'out_of_stock_count': len(out_of_stock_products),
                    'total_inventory_value': float(total_value)
                },
                'categories': categories
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error generando reporte de inventario: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@simple_reports_bp.route('/dashboard', methods=['GET'])
@jwt_required()
@require_permission('report_view')
def get_dashboard_summary():
    """Obtener resumen para dashboard"""
    try:
        # Fechas para diferentes períodos
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        # Ventas de hoy
        today_sales = db.session.query(func.count(Sale.id), func.coalesce(func.sum(Sale.total_amount), 0)).filter(
            func.date(Sale.created_at) == today
        ).first()
        
        # Ventas de ayer
        yesterday_sales = db.session.query(func.count(Sale.id), func.coalesce(func.sum(Sale.total_amount), 0)).filter(
            func.date(Sale.created_at) == yesterday
        ).first()
        
        # Ventas de la semana
        week_sales = db.session.query(func.count(Sale.id), func.coalesce(func.sum(Sale.total_amount), 0)).filter(
            Sale.created_at >= week_ago
        ).first()
        
        # Ventas del mes
        month_sales = db.session.query(func.count(Sale.id), func.coalesce(func.sum(Sale.total_amount), 0)).filter(
            Sale.created_at >= month_ago
        ).first()
        
        # Productos más vendidos (último mes)
        top_products = db.session.query(
            Product.name,
            func.sum(SaleItem.quantity).label('total_sold'),
            func.sum(SaleItem.subtotal).label('total_revenue')
        ).join(SaleItem).join(Sale).filter(
            Sale.created_at >= month_ago
        ).group_by(Product.id, Product.name).order_by(
            desc(func.sum(SaleItem.quantity))
        ).limit(5).all()
        
        # Productos con stock bajo
        low_stock = db.session.query(Product).filter(
            and_(
                Product.is_active == True,
                Product.stock <= func.coalesce(Product.min_stock, 5)
            )
        ).count()
        
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
                'sales_month': {
                    'count': month_sales[0] or 0,
                    'total': float(month_sales[1] or 0)
                },
                'top_products': [
                    {
                        'name': product[0],
                        'quantity_sold': int(product[1]),
                        'revenue': float(product[2])
                    } for product in top_products
                ],
                'alerts': {
                    'low_stock_count': low_stock
                }
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error generando resumen de dashboard: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@simple_reports_bp.route('/products/performance', methods=['GET'])
@jwt_required()
@require_permission('report_view')
def get_product_performance():
    """Obtener rendimiento de productos"""
    try:
        days = int(request.args.get('days', 30))
        limit = int(request.args.get('limit', 20))
        
        # Fecha de inicio
        start_date = datetime.now() - timedelta(days=days)
        
        # Productos más vendidos
        top_products = db.session.query(
            Product.id,
            Product.name,
            Product.category,
            Product.price,
            func.sum(SaleItem.quantity).label('total_sold'),
            func.sum(SaleItem.subtotal).label('total_revenue'),
            func.count(Sale.id).label('sale_count')
        ).join(SaleItem).join(Sale).filter(
            Sale.created_at >= start_date
        ).group_by(
            Product.id, Product.name, Product.category, Product.price
        ).order_by(
            desc(func.sum(SaleItem.quantity))
        ).limit(limit).all()
        
        products_data = []
        for product in top_products:
            products_data.append({
                'id': product.id,
                'name': product.name,
                'category': product.category,
                'price': float(product.price),
                'quantity_sold': int(product.total_sold),
                'revenue': float(product.total_revenue),
                'sale_count': int(product.sale_count),
                'avg_per_sale': float(product.total_sold) / int(product.sale_count) if product.sale_count > 0 else 0
            })
        
        response_data = {
            'success': True,
            'data': {
                'products': products_data,
                'period_days': days,
                'total_products': len(products_data)
            }
        }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error generando reporte de rendimiento: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

@simple_reports_bp.route('/export/<string:report_type>', methods=['POST'])
@jwt_required()
@require_permission('report_export')
def export_report(report_type):
    """Exportar reportes en formato CSV"""
    try:
        data = request.get_json()
        
        if report_type == 'sales':
            # Exportar ventas
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            
            if not start_date:
                start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
                
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            
            sales = db.session.query(
                Sale.id,
                Sale.created_at,
                Sale.total_amount,
                Sale.payment_method,
                User.username
            ).join(User).filter(
                and_(Sale.created_at >= start_dt, Sale.created_at < end_dt)
            ).all()
            
            # Crear CSV
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Fecha', 'Total', 'Método Pago', 'Cliente', 'Vendedor'])
            
            for sale in sales:
                writer.writerow([
                    sale.id,
                    sale.created_at.strftime('%Y-%m-%d %H:%M'),
                    sale.total_amount,
                    sale.payment_method or 'Efectivo',
                    '',  # customer_name no está disponible en este modelo
                    sale.username
                ])
            
            csv_data = output.getvalue()
            output.close()
            
            return jsonify({
                'success': True,
                'data': csv_data,
                'filename': f'ventas_{start_date}_to_{end_date}.csv'
            }), 200
            
        elif report_type == 'inventory':
            # Exportar inventario
            products = db.session.query(Product).filter(
                Product.is_active == True
            ).order_by(Product.category, Product.name).all()
            
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Nombre', 'SKU', 'Categoría', 'Precio', 'Stock', 'Stock Mínimo', 'Valor Total'])
            
            for product in products:
                writer.writerow([
                    product.id,
                    product.name,
                    product.sku or '',
                    product.category or '',
                    product.price,
                    product.stock,
                    product.min_stock or 5,
                    product.price * product.stock
                ])
            
            csv_data = output.getvalue()
            output.close()
            
            return jsonify({
                'success': True,
                'data': csv_data,
                'filename': f'inventario_{datetime.now().strftime("%Y%m%d")}.csv'
            }), 200
            
        else:
            return jsonify({
                'success': False,
                'error': 'Tipo de reporte no válido'
            }), 400
            
    except Exception as e:
        logger.error(f"Error exportando reporte {report_type}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error interno del servidor',
            'message': str(e)
        }), 500

# Error handlers
@simple_reports_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado',
        'message': 'El endpoint solicitado no existe'
    }), 404

@simple_reports_bp.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor',
        'message': 'Ha ocurrido un error inesperado'
    }), 500
