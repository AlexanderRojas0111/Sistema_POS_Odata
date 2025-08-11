from app.models import Sale, Product
from app.core.database import db
from app.schemas import SaleCreate, SaleUpdate
from typing import List, Optional
from datetime import datetime, date

class SalesCRUD:
    """Clase para operaciones CRUD de ventas"""
    
    def get_all(self, page: int = 1, per_page: int = 20) -> List[Sale]:
        """Obtener todas las ventas con paginación"""
        return Sale.query.paginate(
            page=page, per_page=per_page, error_out=False
        ).items
    
    def get(self, sale_id: int) -> Optional[Sale]:
        """Obtener una venta específica"""
        return Sale.query.get(sale_id)
    
    def create(self, sale_data: SaleCreate) -> Sale:
        """Crear una nueva venta"""
        sale = Sale(
            product_id=sale_data.product_id,
            quantity=sale_data.quantity,
            total=sale_data.total,
            user_id=sale_data.user_id,
            customer_id=sale_data.customer_id
        )
        
        # Verificar y actualizar stock del producto
        product = Product.query.get(sale.product_id)
        if product:
            if product.stock < sale.quantity:
                raise ValueError('Stock insuficiente para la venta')
            product.stock -= sale.quantity
        
        db.session.add(sale)
        return sale
    
    def update(self, sale_id: int, sale_data: SaleUpdate) -> Optional[Sale]:
        """Actualizar una venta"""
        sale = self.get(sale_id)
        if not sale:
            return None
        
        if sale_data.quantity is not None:
            sale.quantity = sale_data.quantity
        if sale_data.total is not None:
            sale.total = sale_data.total
        if sale_data.customer_id is not None:
            sale.customer_id = sale_data.customer_id
        
        return sale
    
    def delete(self, sale_id: int) -> bool:
        """Eliminar una venta"""
        sale = self.get(sale_id)
        if not sale:
            return False
        
        db.session.delete(sale)
        return True
    
    def get_today_sales(self) -> List[Sale]:
        """Obtener ventas del día actual"""
        today = date.today()
        return Sale.query.filter(
            Sale.created_at >= today
        ).all()
    
    def get_daily_report(self, report_date: str = None) -> dict:
        """Obtener reporte diario de ventas"""
        if report_date:
            target_date = datetime.strptime(report_date, '%Y-%m-%d').date()
        else:
            target_date = date.today()
        
        sales = Sale.query.filter(
            Sale.created_at >= target_date
        ).all()
        
        total_sales = sum(sale.total for sale in sales)
        total_items = sum(sale.quantity for sale in sales)
        
        return {
            'date': target_date.isoformat(),
            'total_sales': total_sales,
            'total_items': total_items,
            'sales_count': len(sales)
        }
    
    def get_monthly_report(self, year: int, month: int) -> dict:
        """Obtener reporte mensual de ventas"""
        start_date = date(year, month, 1)
        if month == 12:
            end_date = date(year + 1, 1, 1)
        else:
            end_date = date(year, month + 1, 1)
        
        sales = Sale.query.filter(
            Sale.created_at >= start_date,
            Sale.created_at < end_date
        ).all()
        
        total_sales = sum(sale.total for sale in sales)
        total_items = sum(sale.quantity for sale in sales)
        
        return {
            'year': year,
            'month': month,
            'total_sales': total_sales,
            'total_items': total_items,
            'sales_count': len(sales)
        }

# Instancia global del CRUD
sales_crud = SalesCRUD() 