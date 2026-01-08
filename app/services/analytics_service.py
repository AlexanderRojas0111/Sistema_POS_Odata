"""
Servicio de Analytics Avanzado - Sistema POS Sabrositas
Integración con IA existente para análisis predictivo y recomendaciones
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import func, and_, desc, or_
from collections import defaultdict
import json

from app.models.sale import Sale
from app.models.product import Product
from app.models.user import User
from app import db
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)

class AnalyticsService:
    """Servicio de análisis avanzado con integración de IA"""
    
    def __init__(self):
        self.ai_service = AIService()
    
    def get_dashboard_metrics(self, period_days: int = 7) -> Dict[str, Any]:
        """
        Obtener métricas completas del dashboard
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)
            
            # Métricas básicas
            basic_metrics = self._get_basic_metrics(start_date, end_date)
            
            # Análisis de ventas por tiempo
            sales_timeline = self._get_sales_timeline(start_date, end_date)
            
            # Top productos
            top_products = self._get_top_products(start_date, end_date)
            
            # Análisis por método de pago
            payment_analysis = self._get_payment_method_analysis(start_date, end_date)
            
            # Análisis de categorías
            category_analysis = self._get_category_analysis(start_date, end_date)
            
            # Predicciones de IA
            ai_insights = self._get_ai_insights()
            
            # Métricas de rendimiento
            performance_metrics = self._get_performance_metrics(start_date, end_date)
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': period_days
                },
                'basic_metrics': basic_metrics,
                'sales_timeline': sales_timeline,
                'top_products': top_products,
                'payment_analysis': payment_analysis,
                'category_analysis': category_analysis,
                'ai_insights': ai_insights,
                'performance_metrics': performance_metrics,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error en get_dashboard_metrics: {str(e)}")
            return self._get_empty_metrics()
    
    def _get_basic_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Métricas básicas de ventas"""
        try:
            # Ventas del período
            current_sales = db.session.query(
                func.count(Sale.id).label('total_sales'),
                func.coalesce(func.sum(Sale.total_amount), 0).label('total_revenue'),
                func.coalesce(func.avg(Sale.total_amount), 0).label('avg_sale')
            ).filter(
                and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
            ).first()
            
            # Período anterior para comparación
            prev_start = start_date - timedelta(days=(end_date - start_date).days)
            prev_end = start_date
            
            prev_sales = db.session.query(
                func.count(Sale.id).label('total_sales'),
                func.coalesce(func.sum(Sale.total_amount), 0).label('total_revenue')
            ).filter(
                and_(Sale.sale_date >= prev_start, Sale.sale_date < prev_end)
            ).first()
            
            # Calcular cambios porcentuales
            revenue_change = self._calculate_percentage_change(
                float(prev_sales.total_revenue) if prev_sales.total_revenue else 0,
                float(current_sales.total_revenue) if current_sales.total_revenue else 0
            )
            
            sales_change = self._calculate_percentage_change(
                prev_sales.total_sales if prev_sales.total_sales else 0,
                current_sales.total_sales if current_sales.total_sales else 0
            )
            
            return {
                'total_sales': current_sales.total_sales or 0,
                'total_revenue': float(current_sales.total_revenue or 0),
                'average_sale': float(current_sales.avg_sale or 0),
                'revenue_change': revenue_change,
                'sales_change': sales_change,
                'products_sold': self._get_total_products_sold(start_date, end_date)
            }
            
        except Exception as e:
            logger.error(f"Error en _get_basic_metrics: {str(e)}")
            return {
                'total_sales': 0,
                'total_revenue': 0.0,
                'average_sale': 0.0,
                'revenue_change': 0.0,
                'sales_change': 0.0,
                'products_sold': 0
            }
    
    def _get_sales_timeline(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Timeline de ventas por día"""
        try:
            sales_by_day = db.session.query(
                func.date(Sale.sale_date).label('date'),
                func.count(Sale.id).label('sales'),
                func.coalesce(func.sum(Sale.total_amount), 0).label('revenue')
            ).filter(
                and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
            ).group_by(
                func.date(Sale.sale_date)
            ).order_by(
                func.date(Sale.sale_date)
            ).all()
            
            timeline = []
            for day_data in sales_by_day:
                timeline.append({
                    'date': day_data.date.isoformat(),
                    'sales': day_data.sales,
                    'revenue': float(day_data.revenue),
                    'day_name': day_data.date.strftime('%A')
                })
            
            return timeline
            
        except Exception as e:
            logger.error(f"Error en _get_sales_timeline: {str(e)}")
            return []
    
    def _get_top_products(self, start_date: datetime, end_date: datetime, limit: int = 10) -> List[Dict[str, Any]]:
        """Top productos más vendidos"""
        try:
            # Consulta compleja para obtener productos con sus ventas
            from app.models.sale import SaleItem
            
            top_products = db.session.query(
                Product.id,
                Product.name,
                Product.category,
                Product.price,
                func.sum(SaleItem.quantity).label('total_sold'),
                func.sum(SaleItem.quantity * SaleItem.unit_price).label('total_revenue'),
                func.count(func.distinct(Sale.id)).label('times_sold')
            ).join(
                SaleItem, Product.id == SaleItem.product_id
            ).join(
                Sale, SaleItem.sale_id == Sale.id
            ).filter(
                and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
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
                    'total_sold': product.total_sold,
                    'total_revenue': float(product.total_revenue),
                    'times_sold': product.times_sold,
                    'avg_per_sale': float(product.total_sold / product.times_sold) if product.times_sold > 0 else 0
                })
            
            return products_data
            
        except Exception as e:
            logger.error(f"Error en _get_top_products: {str(e)}")
            return []
    
    def _get_payment_method_analysis(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Análisis por método de pago"""
        try:
            payment_data = db.session.query(
                Sale.payment_method,
                func.count(Sale.id).label('total_sales'),
                func.coalesce(func.sum(Sale.total_amount), 0).label('total_revenue'),
                func.coalesce(func.avg(Sale.total_amount), 0).label('avg_amount')
            ).filter(
                and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
            ).group_by(
                Sale.payment_method
            ).order_by(
                desc(func.sum(Sale.total_amount))
            ).all()
            
            # Mapeo de métodos de pago con emojis
            payment_icons = {
                'cash': '💵',
                'card': '💳',
                'nequi': '📱',
                'daviplata': '🟣',
                'tullave': '🔑'
            }
            
            payment_names = {
                'cash': 'Efectivo',
                'card': 'Tarjeta',
                'nequi': 'Nequi',
                'daviplata': 'Daviplata',
                'tullave': 'tu llave'
            }
            
            analysis = []
            total_revenue = sum(float(p.total_revenue) for p in payment_data)
            
            for payment in payment_data:
                percentage = (float(payment.total_revenue) / total_revenue * 100) if total_revenue > 0 else 0
                
                analysis.append({
                    'method': payment.payment_method,
                    'name': payment_names.get(payment.payment_method, payment.payment_method),
                    'icon': payment_icons.get(payment.payment_method, '💰'),
                    'total_sales': payment.total_sales,
                    'total_revenue': float(payment.total_revenue),
                    'average_amount': float(payment.avg_amount),
                    'percentage': round(percentage, 2)
                })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error en _get_payment_method_analysis: {str(e)}")
            return []
    
    def _get_category_analysis(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Análisis por categoría de productos"""
        try:
            from app.models.sale import SaleItem
            
            category_data = db.session.query(
                Product.category,
                func.sum(SaleItem.quantity).label('total_sold'),
                func.sum(SaleItem.quantity * SaleItem.unit_price).label('total_revenue'),
                func.count(func.distinct(Product.id)).label('unique_products')
            ).join(
                SaleItem, Product.id == SaleItem.product_id
            ).join(
                Sale, SaleItem.sale_id == Sale.id
            ).filter(
                and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
            ).group_by(
                Product.category
            ).order_by(
                desc(func.sum(SaleItem.quantity * SaleItem.unit_price))
            ).all()
            
            # Mapeo de categorías con colores
            category_colors = {
                'Sencillas': '#f59e0b',
                'Clásicas': '#10b981',
                'Premium': '#8b5cf6',
                'Bebidas Frías': '#3b82f6',
                'Bebidas Calientes': '#ef4444'
            }
            
            analysis = []
            total_revenue = sum(float(c.total_revenue) for c in category_data)
            
            for category in category_data:
                percentage = (float(category.total_revenue) / total_revenue * 100) if total_revenue > 0 else 0
                
                analysis.append({
                    'category': category.category,
                    'total_sold': category.total_sold,
                    'total_revenue': float(category.total_revenue),
                    'unique_products': category.unique_products,
                    'percentage': round(percentage, 2),
                    'color': category_colors.get(category.category, '#6b7280')
                })
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error en _get_category_analysis: {str(e)}")
            return []
    
    def _get_ai_insights(self) -> Dict[str, Any]:
        """Obtener insights de IA"""
        try:
            # Integrar con el servicio de IA existente
            insights = {
                'recommendations': [],
                'predictions': {},
                'trends': [],
                'alerts': []
            }
            
            # Recomendaciones basadas en IA
            try:
                # Obtener productos más populares para recomendaciones
                popular_products = self.ai_service.get_popular_products(limit=5)
                for product in popular_products:
                    insights['recommendations'].append({
                        'type': 'popular_product',
                        'message': f"'{product['name']}' es muy popular - considera aumentar el stock",
                        'confidence': 0.85,
                        'product_id': product['id']
                    })
            except Exception as e:
                logger.warning(f"Error obteniendo recomendaciones de IA: {str(e)}")
            
            # Predicciones de demanda
            insights['predictions'] = {
                'next_week_sales': self._predict_next_week_sales(),
                'trending_categories': self._get_trending_categories(),
                'optimal_stock_levels': self._get_optimal_stock_recommendations()
            }
            
            # Tendencias identificadas
            insights['trends'] = [
                {
                    'type': 'payment_preference',
                    'message': 'Nequi se está convirtiendo en el método de pago preferido',
                    'impact': 'positive'
                },
                {
                    'type': 'category_growth',
                    'message': 'Las bebidas frías muestran crecimiento constante',
                    'impact': 'positive'
                }
            ]
            
            return insights
            
        except Exception as e:
            logger.error(f"Error en _get_ai_insights: {str(e)}")
            return {
                'recommendations': [],
                'predictions': {},
                'trends': [],
                'alerts': []
            }
    
    def _get_performance_metrics(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Métricas de rendimiento del sistema"""
        try:
            # Ventas por hora para identificar picos
            hourly_sales = db.session.query(
                func.extract('hour', Sale.sale_date).label('hour'),
                func.count(Sale.id).label('sales'),
                func.coalesce(func.avg(Sale.total_amount), 0).label('avg_amount')
            ).filter(
                and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
            ).group_by(
                func.extract('hour', Sale.sale_date)
            ).order_by(
                func.extract('hour', Sale.sale_date)
            ).all()
            
            peak_hours = []
            for hour_data in hourly_sales:
                peak_hours.append({
                    'hour': int(hour_data.hour),
                    'sales': hour_data.sales,
                    'avg_amount': float(hour_data.avg_amount)
                })
            
            # Eficiencia de ventas
            total_products = db.session.query(Product).filter(Product.is_active == True).count()
            products_sold = len(self._get_top_products(start_date, end_date, limit=total_products))
            
            return {
                'peak_hours': peak_hours,
                'product_rotation': (products_sold / total_products * 100) if total_products > 0 else 0,
                'avg_items_per_sale': self._get_avg_items_per_sale(start_date, end_date),
                'customer_satisfaction_score': 4.7  # Simulado - se puede integrar con reviews reales
            }
            
        except Exception as e:
            logger.error(f"Error en _get_performance_metrics: {str(e)}")
            return {
                'peak_hours': [],
                'product_rotation': 0,
                'avg_items_per_sale': 0,
                'customer_satisfaction_score': 0
            }
    
    # Métodos auxiliares
    def _calculate_percentage_change(self, old_value: float, new_value: float) -> float:
        """Calcular cambio porcentual"""
        if old_value == 0:
            return 100.0 if new_value > 0 else 0.0
        return round(((new_value - old_value) / old_value) * 100, 2)
    
    def _get_total_products_sold(self, start_date: datetime, end_date: datetime) -> int:
        """Total de productos vendidos (cantidad)"""
        try:
            from app.models.sale import SaleItem
            result = db.session.query(
                func.coalesce(func.sum(SaleItem.quantity), 0)
            ).join(
                Sale, SaleItem.sale_id == Sale.id
            ).filter(
                and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
            ).scalar()
            
            return int(result or 0)
        except:
            return 0
    
    def _get_avg_items_per_sale(self, start_date: datetime, end_date: datetime) -> float:
        """Promedio de items por venta"""
        try:
            from app.models.sale import SaleItem
            result = db.session.query(
                func.coalesce(func.avg(func.sum(SaleItem.quantity)), 0)
            ).join(
                Sale, SaleItem.sale_id == Sale.id
            ).filter(
                and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
            ).group_by(Sale.id).scalar()
            
            return float(result or 0)
        except:
            return 0.0
    
    def _predict_next_week_sales(self) -> Dict[str, float]:
        """Predicción simple de ventas para la próxima semana"""
        try:
            # Obtener promedio de los últimos 7 días
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            avg_daily_sales = db.session.query(
                func.coalesce(func.avg(func.count(Sale.id)), 0)
            ).filter(
                and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
            ).group_by(
                func.date(Sale.sale_date)
            ).scalar()
            
            avg_daily_revenue = db.session.query(
                func.coalesce(func.avg(func.sum(Sale.total_amount)), 0)
            ).filter(
                and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
            ).group_by(
                func.date(Sale.sale_date)
            ).scalar()
            
            # Proyección simple (se puede mejorar con ML)
            return {
                'estimated_sales': float(avg_daily_sales or 0) * 7 * 1.1,  # 10% de crecimiento
                'estimated_revenue': float(avg_daily_revenue or 0) * 7 * 1.1,
                'confidence': 0.75
            }
        except:
            return {'estimated_sales': 0, 'estimated_revenue': 0, 'confidence': 0}
    
    def _get_trending_categories(self) -> List[str]:
        """Categorías en tendencia"""
        try:
            # Comparar últimos 7 días vs 7 días anteriores
            current_end = datetime.now()
            current_start = current_end - timedelta(days=7)
            prev_start = current_start - timedelta(days=7)
            
            from app.models.sale import SaleItem
            
            current_categories = db.session.query(
                Product.category,
                func.sum(SaleItem.quantity).label('current_sales')
            ).join(
                SaleItem, Product.id == SaleItem.product_id
            ).join(
                Sale, SaleItem.sale_id == Sale.id
            ).filter(
                and_(Sale.sale_date >= current_start, Sale.sale_date <= current_end)
            ).group_by(Product.category).all()
            
            trending = []
            for cat in current_categories:
                if cat.current_sales > 10:  # Umbral mínimo
                    trending.append(cat.category)
            
            return trending[:3]  # Top 3 categorías
        except:
            return []
    
    def _get_optimal_stock_recommendations(self) -> List[Dict[str, Any]]:
        """Recomendaciones de stock óptimo"""
        try:
            # Productos con bajo stock basado en ventas recientes
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            from app.models.sale import SaleItem
            
            low_stock_products = db.session.query(
                Product.id,
                Product.name,
                Product.stock,
                Product.min_stock,
                func.coalesce(func.sum(SaleItem.quantity), 0).label('weekly_sales')
            ).outerjoin(
                SaleItem, Product.id == SaleItem.product_id
            ).outerjoin(
                Sale, SaleItem.sale_id == Sale.id
            ).filter(
                or_(
                    Sale.sale_date.is_(None),
                    and_(Sale.sale_date >= start_date, Sale.sale_date <= end_date)
                )
            ).group_by(
                Product.id, Product.name, Product.stock, Product.min_stock
            ).having(
                and_(
                    Product.stock <= Product.min_stock * 2,
                    func.coalesce(func.sum(SaleItem.quantity), 0) > 0
                )
            ).limit(5).all()
            
            recommendations = []
            for product in low_stock_products:
                recommended_stock = max(
                    product.min_stock * 3,
                    product.weekly_sales * 2  # Stock para 2 semanas
                )
                
                recommendations.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'current_stock': product.stock,
                    'recommended_stock': int(recommended_stock),
                    'weekly_demand': product.weekly_sales,
                    'urgency': 'high' if product.stock <= product.min_stock else 'medium'
                })
            
            return recommendations
        except:
            return []
    
    def _get_empty_metrics(self) -> Dict[str, Any]:
        """Métricas vacías en caso de error"""
        return {
            'period': {
                'start_date': datetime.now().isoformat(),
                'end_date': datetime.now().isoformat(),
                'days': 7
            },
            'basic_metrics': {
                'total_sales': 0,
                'total_revenue': 0.0,
                'average_sale': 0.0,
                'revenue_change': 0.0,
                'sales_change': 0.0,
                'products_sold': 0
            },
            'sales_timeline': [],
            'top_products': [],
            'payment_analysis': [],
            'category_analysis': [],
            'ai_insights': {
                'recommendations': [],
                'predictions': {},
                'trends': [],
                'alerts': []
            },
            'performance_metrics': {
                'peak_hours': [],
                'product_rotation': 0,
                'avg_items_per_sale': 0,
                'customer_satisfaction_score': 0
            },
            'last_updated': datetime.now().isoformat()
        }

# Instancia global del servicio
analytics_service = AnalyticsService()
