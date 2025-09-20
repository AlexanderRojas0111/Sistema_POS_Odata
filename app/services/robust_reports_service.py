"""
Servicio de Reportes Robusto - Sistema POS Sabrositas
Implementación robusta que funciona con la infraestructura existente
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import func, and_, desc
import csv
import io

from app import db
from app.models.sale import Sale, SaleItem
from app.models.product import Product
from app.models.user import User

logger = logging.getLogger(__name__)

class RobustReportsService:
    """Servicio robusto de reportes que funciona con la estructura existente"""
    
    def generate_sales_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generar reporte de ventas robusto
        """
        try:
            # Consulta base de ventas
            sales = Sale.query.filter(
                and_(Sale.created_at >= start_date, Sale.created_at <= end_date)
            ).order_by(desc(Sale.created_at)).all()
            
            # Estadísticas básicas
            total_sales = len(sales)
            total_revenue = sum(float(sale.total_amount) for sale in sales)
            average_sale = total_revenue / total_sales if total_sales > 0 else 0
            
            # Ventas por método de pago
            payment_methods = {}
            for sale in sales:
                method = sale.payment_method or 'unknown'
                if method not in payment_methods:
                    payment_methods[method] = {'count': 0, 'total': 0}
                payment_methods[method]['count'] += 1
                payment_methods[method]['total'] += float(sale.total_amount)
            
            # Ventas por día
            daily_sales = {}
            for sale in sales:
                if sale.created_at:
                    date_key = sale.created_at.date().isoformat()
                    if date_key not in daily_sales:
                        daily_sales[date_key] = {'sales': 0, 'revenue': 0}
                    daily_sales[date_key]['sales'] += 1
                    daily_sales[date_key]['revenue'] += float(sale.total_amount)
            
            # Productos más vendidos
            product_sales = {}
            for sale in sales:
                for item in sale.items:
                    product_id = item.product_id
                    if product_id not in product_sales:
                        product_sales[product_id] = {
                            'name': 'Producto Desconocido',
                            'quantity': 0,
                            'revenue': 0
                        }
                    
                    # Obtener nombre del producto
                    try:
                        product = Product.query.get(product_id)
                        if product:
                            product_sales[product_id]['name'] = product.name
                    except:
                        pass
                    
                    product_sales[product_id]['quantity'] += item.quantity
                    product_sales[product_id]['revenue'] += float(item.quantity * item.unit_price)
            
            # Ordenar productos por cantidad vendida
            top_products = sorted(
                [{'id': pid, **data} for pid, data in product_sales.items()],
                key=lambda x: x['quantity'],
                reverse=True
            )[:10]
            
            return {
                'report_info': {
                    'type': 'sales',
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'generated_at': datetime.utcnow().isoformat(),
                    'period_days': (end_date - start_date).days + 1
                },
                'summary': {
                    'total_sales': total_sales,
                    'total_revenue': total_revenue,
                    'average_sale': average_sale,
                    'growth_rate': self._calculate_growth_rate(start_date, end_date)
                },
                'sales_detail': [
                    {
                        'id': sale.id,
                        'date': sale.created_at.isoformat() if sale.created_at else None,
                        'total_amount': float(sale.total_amount),
                        'payment_method': sale.payment_method,
                        'customer_name': getattr(sale, 'customer_name', None),
                        'items_count': len(sale.items)
                    }
                    for sale in sales[:50]  # Limitar para performance
                ],
                'payment_methods': [
                    {
                        'method': method,
                        'count': data['count'],
                        'total': data['total'],
                        'percentage': (data['total'] / total_revenue * 100) if total_revenue > 0 else 0
                    }
                    for method, data in payment_methods.items()
                ],
                'daily_sales': [
                    {
                        'date': date,
                        'sales': data['sales'],
                        'revenue': data['revenue']
                    }
                    for date, data in sorted(daily_sales.items())
                ],
                'top_products': top_products
            }
            
        except Exception as e:
            logger.error(f"Error generating sales report: {str(e)}")
            raise
    
    def generate_inventory_report(self) -> Dict[str, Any]:
        """
        Generar reporte de inventario robusto
        """
        try:
            # Obtener productos activos
            products = Product.query.filter(Product.is_active == True).all()
            
            total_products = len(products)
            low_stock_count = 0
            out_of_stock_count = 0
            total_inventory_value = 0
            
            products_data = []
            
            for product in products:
                # Obtener stock de forma segura
                current_stock = getattr(product, 'stock', 0)
                min_stock = getattr(product, 'min_stock', 0)
                price = float(product.price)
                
                # Calcular estado del stock
                if current_stock == 0:
                    status = 'out_of_stock'
                    out_of_stock_count += 1
                elif current_stock <= min_stock:
                    status = 'low_stock'
                    low_stock_count += 1
                else:
                    status = 'good_stock'
                
                inventory_value = current_stock * price
                total_inventory_value += inventory_value
                
                products_data.append({
                    'id': product.id,
                    'name': product.name,
                    'sku': getattr(product, 'sku', ''),
                    'category': product.category,
                    'current_stock': current_stock,
                    'min_stock': min_stock,
                    'price': price,
                    'inventory_value': inventory_value,
                    'status': status,
                    'needs_reorder': current_stock <= min_stock
                })
            
            return {
                'report_info': {
                    'type': 'inventory',
                    'generated_at': datetime.utcnow().isoformat()
                },
                'summary': {
                    'total_products': total_products,
                    'low_stock_count': low_stock_count,
                    'out_of_stock_count': out_of_stock_count,
                    'total_inventory_value': total_inventory_value
                },
                'products': products_data,
                'low_stock_alerts': [
                    p for p in products_data if p['status'] in ['low_stock', 'out_of_stock']
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating inventory report: {str(e)}")
            raise
    
    def generate_cash_flow_report(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Generar reporte de flujo de caja robusto
        """
        try:
            # Ingresos por ventas
            sales = Sale.query.filter(
                and_(Sale.created_at >= start_date, Sale.created_at <= end_date)
            ).all()
            
            total_income = sum(float(sale.total_amount) for sale in sales)
            
            # Agrupar por día
            daily_income = {}
            for sale in sales:
                if sale.created_at:
                    date_key = sale.created_at.date().isoformat()
                    if date_key not in daily_income:
                        daily_income[date_key] = 0
                    daily_income[date_key] += float(sale.total_amount)
            
            # Ingresos por método de pago
            income_by_method = {}
            for sale in sales:
                method = sale.payment_method or 'unknown'
                if method not in income_by_method:
                    income_by_method[method] = 0
                income_by_method[method] += float(sale.total_amount)
            
            return {
                'report_info': {
                    'type': 'cash_flow',
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'generated_at': datetime.utcnow().isoformat()
                },
                'summary': {
                    'total_income': total_income,
                    'sales_income': total_income,
                    'average_daily_income': total_income / ((end_date - start_date).days + 1)
                },
                'income_by_method': [
                    {
                        'method': method,
                        'total': amount,
                        'percentage': (amount / total_income * 100) if total_income > 0 else 0
                    }
                    for method, amount in income_by_method.items()
                ],
                'daily_flow': [
                    {
                        'date': date,
                        'income': amount
                    }
                    for date, amount in sorted(daily_income.items())
                ]
            }
            
        except Exception as e:
            logger.error(f"Error generating cash flow report: {str(e)}")
            raise
    
    def get_product_performance(self, days: int = 30, limit: int = 20) -> Dict[str, Any]:
        """
        Obtener rendimiento de productos robusto
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Productos más vendidos usando consulta SQL optimizada
            top_products_query = db.session.query(
                Product.id,
                Product.name,
                Product.category,
                Product.price,
                func.sum(SaleItem.quantity).label('total_sold'),
                func.sum(SaleItem.quantity * SaleItem.unit_price).label('total_revenue'),
                func.count(Sale.id.distinct()).label('times_ordered')
            ).join(SaleItem, Product.id == SaleItem.product_id)\
             .join(Sale, SaleItem.sale_id == Sale.id)\
             .filter(and_(Sale.created_at >= start_date, Sale.created_at <= end_date))\
             .group_by(Product.id, Product.name, Product.category, Product.price)\
             .order_by(desc(func.sum(SaleItem.quantity)))\
             .limit(limit)
            
            top_products = top_products_query.all()
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'top_products': [
                    {
                        'id': tp.id,
                        'name': tp.name,
                        'category': tp.category,
                        'price': float(tp.price),
                        'total_sold': tp.total_sold or 0,
                        'total_revenue': float(tp.total_revenue or 0),
                        'times_ordered': tp.times_ordered or 0
                    }
                    for tp in top_products
                ]
            }
            
        except Exception as e:
            logger.error(f"Error getting product performance: {str(e)}")
            raise
    
    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Resumen robusto para dashboard
        """
        try:
            today = datetime.now().date()
            yesterday = today - timedelta(days=1)
            
            # Ventas de hoy
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())
            
            today_sales = Sale.query.filter(
                and_(Sale.created_at >= today_start, Sale.created_at <= today_end)
            ).all()
            
            # Ventas de ayer
            yesterday_start = datetime.combine(yesterday, datetime.min.time())
            yesterday_end = datetime.combine(yesterday, datetime.max.time())
            
            yesterday_sales = Sale.query.filter(
                and_(Sale.created_at >= yesterday_start, Sale.created_at <= yesterday_end)
            ).all()
            
            # Calcular totales
            today_revenue = sum(float(s.total_amount) for s in today_sales)
            yesterday_revenue = sum(float(s.total_amount) for s in yesterday_sales)
            
            # Productos con stock bajo (si el campo existe)
            low_stock_count = 0
            total_products = 0
            try:
                products = Product.query.filter(Product.is_active == True).all()
                total_products = len(products)
                for p in products:
                    if hasattr(p, 'stock') and hasattr(p, 'min_stock'):
                        if p.stock <= p.min_stock:
                            low_stock_count += 1
            except Exception as e:
                logger.warning(f"Error calculating stock alerts: {str(e)}")
            
            return {
                'today': {
                    'total_sales': len(today_sales),
                    'total_revenue': today_revenue
                },
                'yesterday': {
                    'total_sales': len(yesterday_sales),
                    'total_revenue': yesterday_revenue
                },
                'inventory_alerts': {
                    'low_stock_products': low_stock_count,
                    'total_products': total_products
                },
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating dashboard summary: {str(e)}")
            raise
    
    def export_to_csv(self, data: List[Dict[str, Any]], filename: str) -> str:
        """
        Exportar datos a CSV de forma robusta
        """
        try:
            output = io.StringIO()
            
            if not data:
                return ""
            
            # Obtener headers de la primera fila
            headers = list(data[0].keys())
            
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            
            for row in data:
                # Limpiar datos para CSV
                clean_row = {}
                for key, value in row.items():
                    if value is None:
                        clean_row[key] = ''
                    elif isinstance(value, (int, float)):
                        clean_row[key] = value
                    else:
                        clean_row[key] = str(value)
                
                writer.writerow(clean_row)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            return ""
    
    def _calculate_growth_rate(self, start_date: datetime, end_date: datetime) -> float:
        """
        Calcular tasa de crecimiento de forma robusta
        """
        try:
            period_days = (end_date - start_date).days + 1
            prev_start = start_date - timedelta(days=period_days)
            prev_end = start_date - timedelta(days=1)
            
            # Ventas del período actual
            current_sales = Sale.query.filter(
                and_(Sale.created_at >= start_date, Sale.created_at <= end_date)
            ).all()
            current_revenue = sum(float(s.total_amount) for s in current_sales)
            
            # Ventas del período anterior
            previous_sales = Sale.query.filter(
                and_(Sale.created_at >= prev_start, Sale.created_at <= prev_end)
            ).all()
            previous_revenue = sum(float(s.total_amount) for s in previous_sales)
            
            if previous_revenue == 0:
                return 100.0 if current_revenue > 0 else 0.0
            
            return ((current_revenue - previous_revenue) / previous_revenue) * 100
            
        except Exception as e:
            logger.warning(f"Error calculating growth rate: {str(e)}")
            return 0.0

# Instancia global del servicio
robust_reports_service = RobustReportsService()
