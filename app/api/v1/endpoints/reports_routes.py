#!/usr/bin/env python3
"""
Rutas de Reportes - O'Data v2.0.0
==================================

Endpoints para:
- Reportes de ventas
- Reportes de inventario
- Reportes de usuarios
- Reportes financieros
- Exportación de datos

Autor: Sistema POS Odata
Versión: 2.0.0
"""

from flask import Blueprint, request, jsonify
from app.models.product import Product
from app.models.sale import Sale
from app.models.user import User
from app.models.inventory import Inventory
from app.core.database import db
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('reports', __name__, url_prefix='/reports')

@bp.route('/sales/summary', methods=['GET'])
def sales_summary_report():
    """
    Reporte resumen de ventas
    ---
    tags:
      - Reportes
    parameters:
      - name: period
        in: query
        type: string
        description: Período (today, week, month, year)
      - name: start_date
        in: query
        type: string
        description: Fecha de inicio (YYYY-MM-DD)
      - name: end_date
        in: query
        type: string
        description: Fecha de fin (YYYY-MM-DD)
    responses:
      200:
        description: Reporte de ventas
    """
    try:
        period = request.args.get('period', 'month')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Calcular fechas según el período
        if period == 'today':
            start_date = datetime.now().date()
            end_date = start_date
        elif period == 'week':
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)
        elif period == 'year':
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=365)
        
        # Si se proporcionan fechas específicas, usarlas
        if start_date and end_date:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Consulta de ventas
        sales_query = Sale.query.filter(
            func.date(Sale.created_at) >= start_date,
            func.date(Sale.created_at) <= end_date
        )
        
        # Estadísticas básicas
        total_sales = sales_query.count()
        total_amount = sales_query.with_entities(func.sum(Sale.total_amount)).scalar() or 0
        
        # Ventas por día
        daily_sales = db.session.query(
            func.date(Sale.created_at).label('date'),
            func.count(Sale.id).label('count'),
            func.sum(Sale.total_amount).label('amount')
        ).filter(
            func.date(Sale.created_at) >= start_date,
            func.date(Sale.created_at) <= end_date
        ).group_by(func.date(Sale.created_at)).order_by(func.date(Sale.created_at)).all()
        
        # Top productos vendidos
        top_products = db.session.query(
            Product.name,
            func.count(Sale.id).label('sales_count'),
            func.sum(Sale.total_amount).label('total_amount')
        ).join(Sale).filter(
            func.date(Sale.created_at) >= start_date,
            func.date(Sale.created_at) <= end_date
        ).group_by(Product.id, Product.name).order_by(desc(func.count(Sale.id))).limit(10).all()
        
        # Top usuarios vendedores
        top_users = db.session.query(
            User.username,
            func.count(Sale.id).label('sales_count'),
            func.sum(Sale.total_amount).label('total_amount')
        ).join(Sale).filter(
            func.date(Sale.created_at) >= start_date,
            func.date(Sale.created_at) <= end_date
        ).group_by(User.id, User.username).order_by(desc(func.count(Sale.id))).limit(10).all()
        
        report = {
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'summary': {
                'total_sales': total_sales,
                'total_amount': float(total_amount),
                'average_amount': float(total_amount / total_sales) if total_sales > 0 else 0
            },
            'daily_sales': [
                {
                    'date': str(day.date),
                    'count': day.count,
                    'amount': float(day.amount or 0)
                }
                for day in daily_sales
            ],
            'top_products': [
                {
                    'name': product.name,
                    'sales_count': product.sales_count,
                    'total_amount': float(product.total_amount or 0)
                }
                for product in top_products
            ],
            'top_users': [
                {
                    'username': user.username,
                    'sales_count': user.sales_count,
                    'total_amount': float(user.total_amount or 0)
                }
                for user in top_users
            ]
        }
        
        return jsonify(report), 200
        
    except Exception as e:
        logger.error(f"Error generando reporte de ventas: {e}")
        return jsonify({'error': 'Error generando reporte'}), 500

@bp.route('/inventory/status', methods=['GET'])
def inventory_status_report():
    """
    Reporte de estado del inventario
    ---
    tags:
      - Reportes
    parameters:
      - name: low_stock_threshold
        in: query
        type: integer
        description: Umbral para stock bajo
      - name: out_of_stock
        in: query
        type: boolean
        description: Solo productos sin stock
    responses:
      200:
        description: Reporte de inventario
    """
    try:
        low_stock_threshold = request.args.get('low_stock_threshold', 10, type=int)
        out_of_stock = request.args.get('out_of_stock', False, type=bool)
        
        # Consulta base de inventario
        inventory_query = Inventory.query.join(Product)
        
        if out_of_stock:
            inventory_query = inventory_query.filter(Inventory.quantity == 0)
        else:
            inventory_query = inventory_query.filter(Inventory.quantity <= low_stock_threshold)
        
        # Obtener productos con stock bajo
        low_stock_items = inventory_query.all()
        
        # Agrupar por categoría
        category_summary = {}
        for item in low_stock_items:
            category = item.product.category
            if category not in category_summary:
                category_summary[category] = {
                    'count': 0,
                    'total_value': 0,
                    'items': []
                }
            
            category_summary[category]['count'] += 1
            category_summary[category]['total_value'] += item.product.price * item.quantity
            
            category_summary[category]['items'].append({
                'product_id': item.product.id,
                'product_name': item.product.name,
                'quantity': item.quantity,
                'price': float(item.product.price),
                'total_value': float(item.product.price * item.quantity)
            })
        
        # Productos más vendidos (para sugerir reabastecimiento)
        top_selling = db.session.query(
            Product.id,
            Product.name,
            Product.category,
            func.count(Sale.id).label('sales_count')
        ).join(Sale).group_by(Product.id, Product.name, Product.category).order_by(
            desc(func.count(Sale.id))
        ).limit(20).all()
        
        report = {
            'threshold': low_stock_threshold,
            'out_of_stock_only': out_of_stock,
            'summary': {
                'total_items': len(low_stock_items),
                'categories_affected': len(category_summary),
                'total_value': sum(
                    item.product.price * item.quantity 
                    for item in low_stock_items
                )
            },
            'category_breakdown': category_summary,
            'top_selling_products': [
                {
                    'id': product.id,
                    'name': product.name,
                    'category': product.category,
                    'sales_count': product.sales_count
                }
                for product in top_selling
            ],
            'generated_at': datetime.now().isoformat()
        }
        
        return jsonify(report), 200
        
    except Exception as e:
        logger.error(f"Error generando reporte de inventario: {e}")
        return jsonify({'error': 'Error generando reporte'}), 500

@bp.route('/users/activity', methods=['GET'])
def user_activity_report():
    """
    Reporte de actividad de usuarios
    ---
    tags:
      - Reportes
    parameters:
      - name: period
        in: query
        type: string
        description: Período (week, month, year)
      - name: role
        in: query
        type: string
        description: Filtrar por rol
    responses:
      200:
        description: Reporte de actividad de usuarios
    """
    try:
        period = request.args.get('period', 'month')
        role = request.args.get('role')
        
        # Calcular fechas
        end_date = datetime.now().date()
        if period == 'week':
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            start_date = end_date - timedelta(days=30)
        elif period == 'year':
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Consulta base de usuarios
        users_query = User.query
        
        if role:
            users_query = users_query.filter(User.role == role)
        
        users = users_query.all()
        
        user_activity = []
        for user in users:
            # Ventas del usuario en el período
            user_sales = Sale.query.filter(
                Sale.user_id == user.id,
                func.date(Sale.created_at) >= start_date,
                func.date(Sale.created_at) <= end_date
            )
            
            sales_count = user_sales.count()
            total_amount = user_sales.with_entities(func.sum(Sale.total_amount)).scalar() or 0
            
            # Última actividad
            last_activity = user_sales.order_by(Sale.created_at.desc()).first()
            last_activity_date = last_activity.created_at if last_activity else None
            
            user_activity.append({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role.value,
                'is_active': user.is_active,
                'period_stats': {
                    'sales_count': sales_count,
                    'total_amount': float(total_amount),
                    'average_amount': float(total_amount / sales_count) if sales_count > 0 else 0
                },
                'last_activity': last_activity_date.isoformat() if last_activity_date else None,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        # Ordenar por actividad
        user_activity.sort(key=lambda x: x['period_stats']['sales_count'], reverse=True)
        
        # Estadísticas generales
        total_users = len(users)
        active_users = len([u for u in users if u.is_active])
        total_sales_period = sum(u['period_stats']['sales_count'] for u in user_activity)
        total_amount_period = sum(u['period_stats']['total_amount'] for u in user_activity)
        
        report = {
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
            'summary': {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': total_users - active_users,
                'total_sales_period': total_sales_period,
                'total_amount_period': total_amount_period,
                'average_sales_per_user': total_sales_period / total_users if total_users > 0 else 0
            },
            'user_activity': user_activity,
            'generated_at': datetime.now().isoformat()
        }
        
        return jsonify(report), 200
        
    except Exception as e:
        logger.error(f"Error generando reporte de actividad de usuarios: {e}")
        return jsonify({'error': 'Error generando reporte'}), 500

@bp.route('/financial/summary', methods=['GET'])
def financial_summary_report():
    """
    Reporte financiero resumen
    ---
    tags:
      - Reportes
    parameters:
      - name: year
        in: query
        type: integer
        description: Año para el reporte
      - name: month
        in: query
        type: integer
        description: Mes específico (1-12)
    responses:
      200:
        description: Reporte financiero
    """
    try:
        year = request.args.get('year', datetime.now().year, type=int)
        month = request.args.get('month', type=int)
        
        # Construir filtro de fecha
        if month:
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
        else:
            start_date = datetime(year, 1, 1).date()
            end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        
        # Ventas del período
        sales_query = Sale.query.filter(
            func.date(Sale.created_at) >= start_date,
            func.date(Sale.created_at) <= end_date
        )
        
        total_sales = sales_query.count()
        total_revenue = sales_query.with_entities(func.sum(Sale.total_amount)).scalar() or 0
        
        # Ventas por mes (si no se especifica mes)
        monthly_data = []
        if not month:
            for m in range(1, 13):
                month_start = datetime(year, m, 1).date()
                if m == 12:
                    month_end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
                else:
                    month_end = datetime(year, m + 1, 1).date() - timedelta(days=1)
                
                month_sales = Sale.query.filter(
                    func.date(Sale.created_at) >= month_start,
                    func.date(Sale.created_at) <= month_end
                ).count()
                
                month_revenue = Sale.query.filter(
                    func.date(Sale.created_at) >= month_start,
                    func.date(Sale.created_at) <= month_end
                ).with_entities(func.sum(Sale.total_amount)).scalar() or 0
                
                monthly_data.append({
                    'month': m,
                    'month_name': datetime(year, m, 1).strftime('%B'),
                    'sales_count': month_sales,
                    'revenue': float(month_revenue)
                })
        
        # Top categorías por ventas
        top_categories = db.session.query(
            Product.category,
            func.count(Sale.id).label('sales_count'),
            func.sum(Sale.total_amount).label('total_revenue')
        ).join(Sale).filter(
            func.date(Sale.created_at) >= start_date,
            func.date(Sale.created_at) <= end_date
        ).group_by(Product.category).order_by(desc(func.sum(Sale.total_amount))).limit(10).all()
        
        report = {
            'period': {
                'year': year,
                'month': month,
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            },
            'summary': {
                'total_sales': total_sales,
                'total_revenue': float(total_revenue),
                'average_sale': float(total_revenue / total_sales) if total_sales > 0 else 0
            },
            'monthly_breakdown': monthly_data if not month else None,
            'top_categories': [
                {
                    'category': cat.category,
                    'sales_count': cat.sales_count,
                    'total_revenue': float(cat.total_revenue or 0),
                    'percentage': float((cat.total_revenue or 0) / total_revenue * 100) if total_revenue > 0 else 0
                }
                for cat in top_categories
            ],
            'generated_at': datetime.now().isoformat()
        }
        
        return jsonify(report), 200
        
    except Exception as e:
        logger.error(f"Error generando reporte financiero: {e}")
        return jsonify({'error': 'Error generando reporte'}), 500
