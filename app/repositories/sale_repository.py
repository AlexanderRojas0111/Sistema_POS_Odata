"""
Sale Repository - Sistema POS O'Data
===================================
Repository específico para ventas con operaciones especializadas.
"""

from typing import Optional, List, Dict, Any
from app.repositories.base_repository import BaseRepository
from app.models.sale import Sale
from app.exceptions import ValidationError, NotFoundError
from app import db

class SaleRepository(BaseRepository[Sale]):
    """Repository para ventas con operaciones especializadas"""
    
    def __init__(self):
        super().__init__(Sale)
    
    def get_sales_by_user(self, user_id: int, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Obtener ventas por usuario"""
        return self.get_all(page=page, per_page=per_page, user_id=user_id)
    
    def get_sales_by_date_range(self, start_date, end_date, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Obtener ventas por rango de fechas"""
        query = Sale.query.filter(
            Sale.created_at >= start_date,
            Sale.created_at <= end_date
        )
        
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return {
            'items': pagination.items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
    
    def get_sales_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de ventas"""
        from sqlalchemy import func
        from datetime import datetime, date
        
        # Estadísticas generales
        total_sales = self.count()
        total_amount = db.session.query(func.sum(Sale.total_amount)).scalar() or 0
        
        # Ventas del día
        today = date.today()
        today_sales = Sale.query.filter(
            func.date(Sale.created_at) == today
        ).count()
        
        today_amount = Sale.query.filter(
            func.date(Sale.created_at) == today
        ).with_entities(func.sum(Sale.total_amount)).scalar() or 0
        
        # Promedio por venta
        avg_sale_amount = float(total_amount / total_sales) if total_sales > 0 else 0
        
        return {
            'total_sales': total_sales,
            'total_amount': float(total_amount),
            'today_sales': today_sales,
            'today_amount': float(today_amount),
            'average_sale_amount': avg_sale_amount
        }
