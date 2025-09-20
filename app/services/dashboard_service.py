from app.models import db
from app.models.sales import Sale
from app.models.products import Product
from app.models.users import User
from app.models.payroll import Payroll
from app.models.accounts_receivable import Invoice
from app.models.quotation import Quotation
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DashboardService:
    """Servicio para obtener estadísticas del dashboard"""
    
    def get_dashboard_stats(self):
        """Obtener estadísticas generales del dashboard"""
        try:
            # Estadísticas de ventas
            total_sales = db.session.query(func.count(Sale.id)).scalar() or 0
            total_revenue = db.session.query(func.sum(Sale.total)).scalar() or 0
            
            # Ventas del día
            today = datetime.now().date()
            today_sales = db.session.query(func.count(Sale.id)).filter(
                func.date(Sale.created_at) == today
            ).scalar() or 0
            
            today_revenue = db.session.query(func.sum(Sale.total)).filter(
                func.date(Sale.created_at) == today
            ).scalar() or 0
            
            # Estadísticas de productos
            total_products = db.session.query(func.count(Product.id)).scalar() or 0
            low_stock_products = db.session.query(func.count(Product.id)).filter(
                Product.stock <= Product.min_stock
            ).scalar() or 0
            
            # Estadísticas de usuarios
            total_users = db.session.query(func.count(User.id)).scalar() or 0
            active_users = db.session.query(func.count(User.id)).filter(
                User.is_active == True
            ).scalar() or 0
            
            # Estadísticas de nómina
            total_payrolls = db.session.query(func.count(Payroll.id)).scalar() or 0
            
            # Estadísticas de cartera
            total_invoices = db.session.query(func.count(Invoice.id)).scalar() or 0
            pending_invoices = db.session.query(func.count(Invoice.id)).filter(
                Invoice.status == 'pending'
            ).scalar() or 0
            
            # Estadísticas de cotizaciones
            total_quotations = db.session.query(func.count(Quotation.id)).scalar() or 0
            pending_quotations = db.session.query(func.count(Quotation.id)).filter(
                Quotation.status == 'pending'
            ).scalar() or 0
            
            return {
                'sales': {
                    'total_sales': total_sales,
                    'total_revenue': float(total_revenue),
                    'today_sales': today_sales,
                    'today_revenue': float(today_revenue)
                },
                'products': {
                    'total_products': total_products,
                    'low_stock_products': low_stock_products
                },
                'users': {
                    'total_users': total_users,
                    'active_users': active_users
                },
                'payroll': {
                    'total_payrolls': total_payrolls
                },
                'accounts_receivable': {
                    'total_invoices': total_invoices,
                    'pending_invoices': pending_invoices
                },
                'quotations': {
                    'total_quotations': total_quotations,
                    'pending_quotations': pending_quotations
                }
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas del dashboard: {str(e)}")
            raise e
    
    def get_dashboard_summary(self):
        """Obtener resumen general del dashboard"""
        try:
            stats = self.get_dashboard_stats()
            
            # Calcular métricas adicionales
            sales_growth = 0  # Placeholder para crecimiento de ventas
            revenue_growth = 0  # Placeholder para crecimiento de ingresos
            
            return {
                'overview': {
                    'total_revenue': stats['sales']['total_revenue'],
                    'today_revenue': stats['sales']['today_revenue'],
                    'total_sales': stats['sales']['total_sales'],
                    'today_sales': stats['sales']['today_sales'],
                    'sales_growth': sales_growth,
                    'revenue_growth': revenue_growth
                },
                'alerts': {
                    'low_stock_products': stats['products']['low_stock_products'],
                    'pending_invoices': stats['accounts_receivable']['pending_invoices'],
                    'pending_quotations': stats['quotations']['pending_quotations']
                },
                'system_health': {
                    'total_products': stats['products']['total_products'],
                    'active_users': stats['users']['active_users'],
                    'total_payrolls': stats['payroll']['total_payrolls']
                }
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen del dashboard: {str(e)}")
            raise e
