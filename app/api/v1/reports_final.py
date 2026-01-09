"""
API de Reportes Final - Sistema POS Sabrositas
==============================================
Solución definitiva y robusta para el módulo de reportes
SIN dependencias problemáticas de JWT o autenticación compleja
"""

from flask import Blueprint, request, jsonify
from app.middleware.rbac_middleware import require_permission
from datetime import datetime, timedelta
from sqlalchemy import func, and_, desc, text
import logging
import csv
import io
import traceback

from app import db
from app.models.sale import Sale, SaleItem
from app.models.product import Product
from app.models.user import User

logger = logging.getLogger(__name__)

# Blueprint final
reports_final_bp = Blueprint('reports_final', __name__, url_prefix='/reports-final')

# ===============================================
# UTILIDADES COMUNES
# ===============================================


def safe_execute_query(query_func, default_value=None):
    """Ejecutar consulta de forma segura con manejo de errores"""
    try:
        return query_func()
    except Exception as e:
        logger.error(f"Error en consulta: {str(e)}")
        return default_value


def format_currency(amount):
    """Formatear cantidad como moneda"""
    return float(amount) if amount is not None else 0.0


def get_date_range(start_date_str=None, end_date_str=None, default_days=30):
    """Obtener rango de fechas con valores por defecto"""
    if not start_date_str:
        start_date = datetime.now() - timedelta(days=default_days)
    else:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

    if not end_date_str:
        end_date = datetime.now()
    else:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)

    return start_date, end_date

# ===============================================
# ENDPOINTS PRINCIPALES
# ===============================================


@reports_final_bp.route('/health', methods=['GET'])
def health_check():
    """Verificación de salud del módulo"""
    try:
        # Test básico de BD
        test_result = db.session.execute(text('SELECT COUNT(*) FROM sales')).scalar()

        return jsonify({
            'success': True,
            'status': 'healthy',
            'message': 'Módulo de reportes funcionando correctamente',
            'database_connection': 'OK',
            'sales_count': test_result,
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0-final'
        }), 200

    except Exception as e:
        logger.error(f"Error en health_check: {str(e)}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500


@reports_final_bp.route('/sales', methods=['GET'])
@require_permission('reports:read')
def sales_report():
    """Reporte completo de ventas"""
    try:
        # Parámetros
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        include_details = request.args.get('details', 'false').lower() == 'true'

        start_date, end_date = get_date_range(start_date_str, end_date_str)

        # Consulta principal de ventas
        sales_query = db.session.query(Sale).filter(
            and_(
                Sale.created_at >= start_date,
                Sale.created_at < end_date
            )
        ).order_by(desc(Sale.created_at))

        sales = safe_execute_query(lambda: sales_query.all(), [])

        # Procesar estadísticas
        total_sales = len(sales)
        total_revenue = sum(format_currency(sale.total_amount) for sale in sales)
        average_sale = total_revenue / total_sales if total_sales > 0 else 0

        # Estadísticas por método de pago
        payment_methods = {}
        daily_sales = {}
        hourly_sales = {}

        for sale in sales:
            # Por método de pago
            method = sale.payment_method or 'Efectivo'
            if method not in payment_methods:
                payment_methods[method] = {'count': 0, 'total': 0}
            payment_methods[method]['count'] += 1
            payment_methods[method]['total'] += format_currency(sale.total_amount)

            # Por día
            day = sale.created_at.strftime('%Y-%m-%d')
            if day not in daily_sales:
                daily_sales[day] = {'count': 0, 'total': 0}
            daily_sales[day]['count'] += 1
            daily_sales[day]['total'] += format_currency(sale.total_amount)

            # Por hora
            hour = sale.created_at.strftime('%H:00')
            if hour not in hourly_sales:
                hourly_sales[hour] = {'count': 0, 'total': 0}
            hourly_sales[hour]['count'] += 1
            hourly_sales[hour]['total'] += format_currency(sale.total_amount)

        # Preparar respuesta
        response_data = {
            'success': True,
            'data': {
                'summary': {
                    'total_sales': total_sales,
                    'total_revenue': total_revenue,
                    'average_sale': average_sale,
                    'period': {
                        'start': start_date.strftime('%Y-%m-%d'),
                        'end': (end_date - timedelta(days=1)).strftime('%Y-%m-%d'),
                        'days': (end_date - start_date).days
                    }
                },
                'analytics': {
                    'payment_methods': payment_methods,
                    'daily_breakdown': daily_sales,
                    'hourly_breakdown': hourly_sales
                }
            },
            'message': f'Reporte de ventas generado: {total_sales} ventas, ${total_revenue:,.2f}'
        }

        # Incluir detalles si se solicita
        if include_details and sales:
            sales_details = []
            for sale in sales[:100]:  # Limitar a 100 para rendimiento
                try:
                    # Obtener usuario de forma segura
                    user = safe_execute_query(
                        lambda: User.query.get(sale.user_id),
                        None
                    )

                    sale_detail = {
                        'id': sale.id,
                        'date': sale.created_at.isoformat(),
                        'total': format_currency(sale.total_amount),
                        'payment_method': sale.payment_method or 'Efectivo',
                        'seller': user.username if user else 'Desconocido',
                        'status': sale.status
                    }
                    sales_details.append(sale_detail)

                except Exception as e:
                    logger.warning(f"Error procesando venta {sale.id}: {e}")
                    continue

            response_data['data']['sales_details'] = sales_details

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Error en sales_report: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Error generando reporte de ventas',
            'details': str(e)
        }), 500


@reports_final_bp.route('/inventory', methods=['GET'])
@require_permission('reports:read')
def inventory_report():
    """Reporte completo de inventario"""
    try:
        include_details = request.args.get('details', 'false').lower() == 'true'
        category_filter = request.args.get('category')
        stock_filter = request.args.get('stock_status')  # 'low', 'out', 'normal'

        # Query base
        query = db.session.query(Product).filter(Product.is_active.is_(True))

        # Aplicar filtros
        if category_filter:
            query = query.filter(Product.category == category_filter)

        if stock_filter == 'low':
            query = query.filter(Product.stock <= func.coalesce(Product.min_stock, 5))
        elif stock_filter == 'out':
            query = query.filter(Product.stock <= 0)
        elif stock_filter == 'normal':
            query = query.filter(Product.stock > func.coalesce(Product.min_stock, 5))

        products = safe_execute_query(lambda: query.order_by(Product.category, Product.name).all(), [])

        # Procesar estadísticas
        total_products = len(products)
        total_stock_units = sum(product.stock for product in products)
        total_value = sum(format_currency(product.price * product.stock) for product in products)

        low_stock_count = sum(1 for p in products if p.stock <= (p.min_stock or 5))
        out_of_stock_count = sum(1 for p in products if p.stock <= 0)

        # Estadísticas por categoría
        categories = {}
        for product in products:
            category = product.category or 'Sin categoría'
            if category not in categories:
                categories[category] = {
                    'product_count': 0,
                    'total_stock': 0,
                    'total_value': 0,
                    'low_stock_items': 0
                }

            categories[category]['product_count'] += 1
            categories[category]['total_stock'] += product.stock
            categories[category]['total_value'] += format_currency(product.price * product.stock)

            if product.stock <= (product.min_stock or 5):
                categories[category]['low_stock_items'] += 1

        response_data = {
            'success': True,
            'data': {
                'summary': {
                    'total_products': total_products,
                    'total_stock_units': total_stock_units,
                    'total_inventory_value': total_value,
                    'low_stock_count': low_stock_count,
                    'out_of_stock_count': out_of_stock_count,
                    'categories_count': len(categories)
                },
                'categories': categories
            },
            'message': f'Reporte de inventario: {total_products} productos, valor ${total_value:,.2f}'
        }

        # Incluir detalles de productos si se solicita
        if include_details:
            products_details = []
            for product in products[:100]:  # Limitar para rendimiento
                try:
                    stock_status = 'normal'
                    if product.stock <= 0:
                        stock_status = 'out_of_stock'
                    elif product.stock <= (product.min_stock or 5):
                        stock_status = 'low_stock'

                    product_detail = {
                        'id': product.id,
                        'name': product.name,
                        'sku': product.sku or '',
                        'category': product.category or 'Sin categoría',
                        'price': format_currency(product.price),
                        'stock': product.stock,
                        'min_stock': product.min_stock or 5,
                        'stock_value': format_currency(product.price * product.stock),
                        'stock_status': stock_status
                    }
                    products_details.append(product_detail)

                except Exception as e:
                    logger.warning(f"Error procesando producto {product.id}: {e}")
                    continue

            response_data['data']['products_details'] = products_details

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Error en inventory_report: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Error generando reporte de inventario',
            'details': str(e)
        }), 500


@reports_final_bp.route('/dashboard', methods=['GET'])
def dashboard_summary():
    """Dashboard con métricas clave"""
    try:
        # Fechas de referencia
        now = datetime.now()
        today = now.date()
        yesterday = today - timedelta(days=1)
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # Métricas de ventas con manejo seguro
        def get_sales_stats(date_filter):
            return safe_execute_query(
                lambda: db.session.query(
                    func.count(Sale.id),
                    func.coalesce(func.sum(Sale.total_amount), 0)
                ).filter(date_filter).first(),
                (0, 0)
            )

        today_stats = get_sales_stats(func.date(Sale.created_at) == today)
        yesterday_stats = get_sales_stats(func.date(Sale.created_at) == yesterday)
        week_stats = get_sales_stats(Sale.created_at >= week_ago)
        month_stats = get_sales_stats(Sale.created_at >= month_ago)

        # Productos más vendidos (con manejo seguro)
        top_products_raw = safe_execute_query(
            lambda: db.session.query(
                Product.name,
                func.sum(SaleItem.quantity).label('total_sold'),
                func.sum(SaleItem.total_price).label('revenue')
            ).select_from(Product).join(SaleItem).join(Sale).filter(
                Sale.created_at >= month_ago
            ).group_by(Product.id, Product.name).order_by(
                desc(func.sum(SaleItem.quantity))
            ).limit(5).all(),
            []
        )

        top_products = [
            {
                'name': product[0],
                'quantity_sold': int(product[1] or 0),
                'revenue': format_currency(product[2])
            } for product in top_products_raw
        ]

        # Métricas de inventario
        inventory_stats = safe_execute_query(
            lambda: db.session.query(
                func.count(Product.id),
                func.sum(Product.stock),
                func.sum(Product.price * Product.stock)
            ).filter(Product.is_active.is_(True)).first(),
            (0, 0, 0)
        )

        low_stock_count = safe_execute_query(
            lambda: db.session.query(func.count(Product.id)).filter(
                and_(
                    Product.is_active.is_(True),
                    Product.stock <= func.coalesce(Product.min_stock, 5)
                )
            ).scalar(),
            0
        )

        # Calcular tendencias
        def calculate_trend(current, previous):
            if previous > 0:
                return ((current - previous) / previous) * 100
            return 0 if current == 0 else 100

        sales_trend = calculate_trend(
            format_currency(today_stats[1]),
            format_currency(yesterday_stats[1])
        )

        response_data = {
            'success': True,
            'data': {
                'sales_metrics': {
                    'today': {
                        'count': today_stats[0] or 0,
                        'total': format_currency(today_stats[1]),
                        'trend': sales_trend
                    },
                    'yesterday': {
                        'count': yesterday_stats[0] or 0,
                        'total': format_currency(yesterday_stats[1])
                    },
                    'week': {
                        'count': week_stats[0] or 0,
                        'total': format_currency(week_stats[1])
                    },
                    'month': {
                        'count': month_stats[0] or 0,
                        'total': format_currency(month_stats[1])
                    }
                },
                'inventory_metrics': {
                    'total_products': inventory_stats[0] or 0,
                    'total_stock_units': inventory_stats[1] or 0,
                    'total_value': format_currency(inventory_stats[2]),
                    'low_stock_alerts': low_stock_count or 0
                },
                'top_products': top_products,
                'generated_at': now.isoformat()
            },
            'message': 'Dashboard generado exitosamente'
        }

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Error en dashboard_summary: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Error generando dashboard',
            'details': str(e)
        }), 500


@reports_final_bp.route('/products/performance', methods=['GET'])
def product_performance():
    """Análisis de rendimiento de productos"""
    try:
        days = int(request.args.get('days', 30))
        limit = int(request.args.get('limit', 20))
        category = request.args.get('category')

        start_date = datetime.now() - timedelta(days=days)

        # Query base para productos con ventas
        base_query = db.session.query(
            Product.id,
            Product.name,
            Product.category,
            Product.price,
            Product.stock,
            func.coalesce(func.sum(SaleItem.quantity), 0).label('total_sold'),
            func.coalesce(func.sum(SaleItem.total_price), 0).label('total_revenue'),
            func.count(Sale.id).label('transaction_count')
        ).select_from(Product).outerjoin(SaleItem).outerjoin(Sale).filter(
            Product.is_active.is_(True)
        )

        # Filtrar por período de ventas
        base_query = base_query.filter(
            and_(
                Sale.created_at >= start_date,
                Sale.created_at <= datetime.now()
            )
        )

        # Filtrar por categoría si se especifica
        if category:
            base_query = base_query.filter(Product.category == category)

        # Agrupar y ordenar
        products_raw = safe_execute_query(
            lambda: base_query.group_by(
                Product.id, Product.name, Product.category, Product.price, Product.stock
            ).order_by(
                desc(func.coalesce(func.sum(SaleItem.quantity), 0))
            ).limit(limit).all(),
            []
        )

        # Procesar resultados
        products_performance = []
        for product in products_raw:
            total_sold = int(product.total_sold or 0)
            revenue = format_currency(product.total_revenue)
            transactions = int(product.transaction_count or 0)

            # Calcular métricas adicionales
            avg_per_transaction = total_sold / transactions if transactions > 0 else 0
            revenue_per_unit = revenue / total_sold if total_sold > 0 else 0
            stock_turnover = total_sold / product.stock if product.stock > 0 else 0

            product_data = {
                'id': product.id,
                'name': product.name,
                'category': product.category or 'Sin categoría',
                'price': format_currency(product.price),
                'current_stock': product.stock,
                'quantity_sold': total_sold,
                'revenue': revenue,
                'transactions': transactions,
                'metrics': {
                    'avg_per_transaction': round(avg_per_transaction, 2),
                    'revenue_per_unit': round(revenue_per_unit, 2),
                    'stock_turnover': round(stock_turnover, 2)
                }
            }
            products_performance.append(product_data)

        # Estadísticas generales
        total_revenue = sum(p['revenue'] for p in products_performance)
        total_sold = sum(p['quantity_sold'] for p in products_performance)

        response_data = {
            'success': True,
            'data': {
                'products': products_performance,
                'summary': {
                    'period_days': days,
                    'products_analyzed': len(products_performance),
                    'total_units_sold': total_sold,
                    'total_revenue': total_revenue,
                    'category_filter': category or 'Todas'
                }
            },
            'message': f'Análisis de {len(products_performance)} productos (últimos {days} días)'
        }

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Error en product_performance: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Error analizando rendimiento de productos',
            'details': str(e)
        }), 500


@reports_final_bp.route('/export/sales', methods=['GET'])
def export_sales():
    """Exportar ventas en formato CSV"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')

        start_date, end_date = get_date_range(start_date_str, end_date_str)

        # Obtener ventas con información del vendedor
        sales_data = safe_execute_query(
            lambda: db.session.query(
                Sale.id,
                Sale.created_at,
                Sale.total_amount,
                Sale.payment_method,
                Sale.status,
                User.username
            ).join(User, Sale.user_id == User.id).filter(
                and_(
                    Sale.created_at >= start_date,
                    Sale.created_at < end_date
                )
            ).order_by(Sale.created_at).all(),
            []
        )

        # Generar CSV
        output = io.StringIO()
        writer = csv.writer(output)

        # Headers
        writer.writerow([
            'ID Venta', 'Fecha', 'Hora', 'Total', 'Método de pago',
            'Estado', 'Vendedor'
        ])

        # Datos
        for sale in sales_data:
            writer.writerow([
                sale.id,
                sale.created_at.strftime('%Y-%m-%d'),
                sale.created_at.strftime('%H:%M:%S'),
                format_currency(sale.total_amount),
                sale.payment_method or 'Efectivo',
                sale.status,
                sale.username
            ])

        csv_content = output.getvalue()
        output.close()

        filename = f'ventas_{start_date.strftime("%Y%m%d")}_to_{(end_date - timedelta(days=1)).strftime("%Y%m%d")}.csv'

        return jsonify({
            'success': True,
            'data': {
                'csv_content': csv_content,
                'filename': filename,
                'records_count': len(sales_data),
                'generated_at': datetime.now().isoformat()
            },
            'message': f'Exportación CSV generada: {len(sales_data)} registros'
        }), 200

    except Exception as e:
        logger.error(f"Error en export_sales: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Error exportando ventas',
            'details': str(e)
        }), 500

# ===============================================
# ENDPOINTS DE DIAGNÓSTICO
# ===============================================


@reports_final_bp.route('/diagnostics', methods=['GET'])
def system_diagnostics():
    """Diagnósticos completos del sistema"""
    try:
        # Test de conexión a BD
        db_test = safe_execute_query(
            lambda: db.session.execute(text('SELECT 1 as test')).scalar(),
            None
        )

        # Contar registros en tablas principales
        sales_count = safe_execute_query(
            lambda: db.session.query(func.count(Sale.id)).scalar(),
            0
        )

        products_count = safe_execute_query(
            lambda: db.session.query(func.count(Product.id)).filter(Product.is_active.is_(True)).scalar(),
            0
        )

        users_count = safe_execute_query(
            lambda: db.session.query(func.count(User.id)).filter(User.is_active.is_(True)).scalar(),
            0
        )

        # Test de rendimiento de consultas
        start_time = datetime.now()
        _ = safe_execute_query(
            lambda: db.session.query(Sale).limit(10).all(),
            []
        )
        query_time = (datetime.now() - start_time).total_seconds()

        response_data = {
            'success': True,
            'data': {
                'database': {
                    'connection': 'OK' if db_test else 'FAILED',
                    'query_performance': f'{query_time:.3f}s'
                },
                'data_counts': {
                    'sales': sales_count,
                    'products': products_count,
                    'users': users_count
                },
                'system_info': {
                    'timestamp': datetime.now().isoformat(),
                    'module_version': '1.0.0-final',
                    'python_version': '3.9+'
                }
            },
            'message': 'Diagnósticos completados exitosamente'
        }

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"Error en system_diagnostics: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Error ejecutando diagnósticos',
            'details': str(e)
        }), 500
