"""
Consolidated Reporting Service - Sistema Multi-Sede Sabrositas
=============================================================
Servicio para generación de reportes consolidados multi-tienda.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging
from app import db
from app.models.store import Store, StoreProduct
from app.models.product import Product
from app.models.sale import Sale, SaleItem
from app.models.inventory_transfer import InventoryTransfer
from app.exceptions import ValidationError
from sqlalchemy import func, or_
import json

logger = logging.getLogger(__name__)


class ConsolidatedReportingService:
    """Servicio de reportes consolidados multi-sede"""

    def __init__(self):
        self.supported_periods = ['daily', 'weekly', 'monthly', 'quarterly', 'yearly']
        self.supported_formats = ['json', 'csv', 'excel']

    def generate_sales_report(self,
                              start_date: datetime,
                              end_date: datetime,
                              store_ids: List[int] = None,
                              group_by: str = 'store',
                              include_details: bool = False) -> Dict[str, Any]:
        """Generar reporte consolidado de ventas"""
        try:
            # Validar parámetros
            if start_date >= end_date:
                raise ValidationError("start_date debe ser menor que end_date")

            if group_by not in ['store', 'product', 'category', 'user', 'day', 'hour']:
                raise ValidationError("group_by debe ser uno de: store, product, category, user, day, hour")

            # Base query
            query = db.session.query(Sale).filter(
                Sale.created_at >= start_date,
                Sale.created_at <= end_date
            )

            # Filtrar por tiendas si se especifica
            if store_ids:
                query = query.filter(Sale.store_id.in_(store_ids))

            # Obtener ventas base
            sales = query.all()

            # Calcular métricas principales
            total_sales = len(sales)
            total_revenue = sum(float(sale.total) for sale in sales)
            total_tax = sum(float(sale.tax_amount or 0) for sale in sales)
            average_sale = total_revenue / total_sales if total_sales > 0 else 0

            # Generar datos agrupados según group_by
            grouped_data = self._group_sales_data(sales, group_by, include_details)

            # Obtener comparación con período anterior
            previous_period_data = self._get_previous_period_comparison(
                start_date, end_date, store_ids
            )

            return {
                'report_info': {
                    'type': 'sales_report',
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'days': (end_date - start_date).days + 1
                    },
                    'filters': {
                        'store_ids': store_ids,
                        'group_by': group_by,
                        'include_details': include_details
                    },
                    'generated_at': datetime.utcnow().isoformat()
                },
                'summary': {
                    'total_sales': total_sales,
                    'total_revenue': round(total_revenue, 2),
                    'total_tax': round(total_tax, 2),
                    'average_sale_value': round(average_sale, 2),
                    'stores_involved': len(set(sale.store_id for sale in sales)),
                    'unique_customers': len(set(sale.customer_name for sale in sales if sale.customer_name))
                },
                'grouped_data': grouped_data,
                'comparison': previous_period_data,
                'trends': self._calculate_sales_trends(sales, group_by)
            }

        except Exception as e:
            logger.error(f"Error generando reporte de ventas: {e}")
            raise

    def _group_sales_data(self, sales: List[Sale], group_by: str, include_details: bool) -> List[Dict[str, Any]]:
        """Agrupar datos de ventas según criterio especificado"""
        try:
            grouped = {}

            for sale in sales:
                # Determinar clave de agrupación
                if group_by == 'store':
                    key = f"store_{sale.store_id}"
                    label = sale.store.name if sale.store else f"Tienda {sale.store_id}"
                elif group_by == 'product':
                    # Agrupar por productos vendidos
                    for item in sale.sale_items:
                        key = f"product_{item.product_id}"
                        label = item.product.name if item.product else f"Producto {item.product_id}"
                        self._add_to_group(grouped, key, label, sale, item)
                    continue
                elif group_by == 'category':
                    # Agrupar por categorías de productos
                    categories = set()
                    for item in sale.sale_items:
                        if item.product and item.product.category:
                            categories.add(item.product.category)

                    for category in categories:
                        key = f"category_{category}"
                        label = category
                        self._add_to_group(grouped, key, label, sale)
                    continue
                elif group_by == 'user':
                    key = f"user_{sale.user_id}"
                    label = f"{sale.user.first_name} {sale.user.last_name}" if sale.user else f"Usuario {sale.user_id}"
                elif group_by == 'day':
                    key = sale.created_at.strftime('%Y-%m-%d')
                    label = sale.created_at.strftime('%Y-%m-%d')
                elif group_by == 'hour':
                    key = sale.created_at.strftime('%Y-%m-%d %H:00')
                    label = sale.created_at.strftime('%Y-%m-%d %H:00')

                self._add_to_group(grouped, key, label, sale)

            # Convertir a lista y ordenar
            result = []
            for key, data in grouped.items():
                group_info = {
                    'group_key': key,
                    'group_label': data['label'],
                    'total_sales': data['count'],
                    'total_revenue': round(data['revenue'], 2),
                    'total_tax': round(data['tax'], 2),
                    'average_sale': round(data['revenue'] / data['count'] if data['count'] > 0 else 0, 2),
                    'total_items': data['items']
                }

                if include_details:
                    group_info['sales_details'] = [
                        {
                            'sale_id': sale.id,
                            'sale_number': sale.sale_number,
                            'total': float(sale.total),
                            'tax_amount': float(sale.tax_amount or 0),
                            'created_at': sale.created_at.isoformat(),
                            'customer_name': sale.customer_name,
                            'payment_method': sale.payment_method
                        }
                        for sale in data['sales']
                    ]

                result.append(group_info)

            # Ordenar por revenue descendente
            result.sort(key=lambda x: x['total_revenue'], reverse=True)

            return result

        except Exception as e:
            logger.error(f"Error agrupando datos de ventas: {e}")
            raise

    def _add_to_group(self, grouped: Dict, key: str, label: str, sale: Sale, item: SaleItem = None):
        """Agregar venta a grupo específico"""
        if key not in grouped:
            grouped[key] = {
                'label': label,
                'count': 0,
                'revenue': 0,
                'tax': 0,
                'items': 0,
                'sales': []
            }

        grouped[key]['count'] += 1
        grouped[key]['revenue'] += float(sale.total)
        grouped[key]['tax'] += float(sale.tax_amount or 0)
        grouped[key]['items'] += sum(item.quantity for item in sale.sale_items)
        grouped[key]['sales'].append(sale)

    def _get_previous_period_comparison(self,
                                        start_date: datetime,
                                        end_date: datetime,
                                        store_ids: List[int] = None) -> Dict[str, Any]:
        """Obtener comparación con período anterior"""
        try:
            period_length = end_date - start_date
            previous_start = start_date - period_length
            previous_end = start_date

            # Query para período anterior
            query = db.session.query(Sale).filter(
                Sale.created_at >= previous_start,
                Sale.created_at < previous_end
            )

            if store_ids:
                query = query.filter(Sale.store_id.in_(store_ids))

            previous_sales = query.all()

            # Calcular métricas del período anterior
            previous_total_sales = len(previous_sales)
            previous_revenue = sum(float(sale.total) for sale in previous_sales)

            # Calcular cambios porcentuales
            current_query = db.session.query(Sale).filter(
                Sale.created_at >= start_date,
                Sale.created_at <= end_date
            )
            if store_ids:
                current_query = current_query.filter(Sale.store_id.in_(store_ids))

            current_sales = current_query.all()
            current_total_sales = len(current_sales)
            current_revenue = sum(float(sale.total) for sale in current_sales)

            # Calcular cambios
            sales_change = ((current_total_sales - previous_total_sales) /
                            previous_total_sales * 100) if previous_total_sales > 0 else 0
            revenue_change = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0

            return {
                'previous_period': {
                    'start_date': previous_start.isoformat(),
                    'end_date': previous_end.isoformat(),
                    'total_sales': previous_total_sales,
                    'total_revenue': round(previous_revenue, 2)
                },
                'changes': {
                    'sales_change_percentage': round(sales_change, 2),
                    'revenue_change_percentage': round(revenue_change, 2),
                    'sales_trend': 'up' if sales_change > 0 else 'down' if sales_change < 0 else 'stable',
                    'revenue_trend': 'up' if revenue_change > 0 else 'down' if revenue_change < 0 else 'stable'
                }
            }

        except Exception as e:
            logger.warning(f"Error calculando comparación con período anterior: {e}")
            return {'error': 'No se pudo calcular comparación'}

    def _calculate_sales_trends(self, sales: List[Sale], group_by: str) -> Dict[str, Any]:
        """Calcular tendencias de ventas"""
        try:
            if not sales:
                return {'error': 'No hay datos para calcular tendencias'}

            # Agrupar ventas por día para tendencias temporales
            daily_sales = {}
            for sale in sales:
                day_key = sale.created_at.strftime('%Y-%m-%d')
                if day_key not in daily_sales:
                    daily_sales[day_key] = {'count': 0, 'revenue': 0}

                daily_sales[day_key]['count'] += 1
                daily_sales[day_key]['revenue'] += float(sale.total)

            # Convertir a series temporales ordenadas
            sorted_days = sorted(daily_sales.keys())
            daily_counts = [daily_sales[day]['count'] for day in sorted_days]
            daily_revenues = [daily_sales[day]['revenue'] for day in sorted_days]

            # Calcular tendencias simples
            if len(daily_counts) >= 2:
                # Tendencia de ventas (simple: comparar primera y última mitad)
                mid_point = len(daily_counts) // 2
                first_half_avg = sum(daily_counts[:mid_point]) / mid_point if mid_point > 0 else 0
                second_half_avg = sum(daily_counts[mid_point:]) / (len(daily_counts) - mid_point)

                sales_trend = 'increasing' if second_half_avg > first_half_avg else 'decreasing' if second_half_avg < first_half_avg else 'stable'

                # Lo mismo para revenue
                first_half_revenue = sum(daily_revenues[:mid_point]) / mid_point if mid_point > 0 else 0
                second_half_revenue = sum(daily_revenues[mid_point:]) / (len(daily_revenues) - mid_point)

                revenue_trend = 'increasing' if second_half_revenue > first_half_revenue else 'decreasing' if second_half_revenue < first_half_revenue else 'stable'
            else:
                sales_trend = 'insufficient_data'
                revenue_trend = 'insufficient_data'

            return {
                'daily_data': [
                    {
                        'date': day,
                        'sales_count': daily_sales[day]['count'],
                        'revenue': round(daily_sales[day]['revenue'], 2)
                    }
                    for day in sorted_days
                ],
                'trends': {
                    'sales_trend': sales_trend,
                    'revenue_trend': revenue_trend,
                    'peak_day': max(sorted_days, key=lambda d: daily_sales[d]['count']) if sorted_days else None,
                    'peak_revenue_day': max(sorted_days, key=lambda d: daily_sales[d]['revenue']) if sorted_days else None
                }
            }

        except Exception as e:
            logger.warning(f"Error calculando tendencias: {e}")
            return {'error': 'No se pudieron calcular tendencias'}

    def generate_inventory_report(self,
                                  store_ids: List[int] = None,
                                  include_transfers: bool = True,
                                  low_stock_only: bool = False) -> Dict[str, Any]:
        """Generar reporte consolidado de inventario"""
        try:
            # Base query
            query = db.session.query(
                Product.id,
                Product.name,
                Product.sku,
                Product.category,
                Store.id.label('store_id'),
                Store.name.label('store_name'),
                Store.code.label('store_code'),
                StoreProduct.current_stock,
                StoreProduct.min_stock,
                StoreProduct.max_stock,
                StoreProduct.local_price,
                StoreProduct.cost_price,
                StoreProduct.is_available,
                StoreProduct.updated_at
            ).join(StoreProduct).join(Store).filter(
                Store.is_active.is_(True),
                Product.is_active.is_(True)
            )

            # Filtros opcionales
            if store_ids:
                query = query.filter(Store.id.in_(store_ids))

            if low_stock_only:
                query = query.filter(StoreProduct.current_stock <= StoreProduct.min_stock)

            inventory_data = query.order_by(Product.name, Store.name).all()

            # Procesar datos
            products_summary = {}
            stores_summary = {}
            total_inventory_value = 0

            for item in inventory_data:
                # Resumen por producto
                if item.id not in products_summary:
                    products_summary[item.id] = {
                        'product_id': item.id,
                        'product_name': item.name,
                        'sku': item.sku,
                        'category': item.category,
                        'total_stock': 0,
                        'stores_count': 0,
                        'stores_with_stock': 0,
                        'stores_low_stock': 0,
                        'average_price': 0,
                        'total_value': 0,
                        'stores_detail': []
                    }

                products_summary[item.id]['total_stock'] += item.current_stock
                products_summary[item.id]['stores_count'] += 1
                products_summary[item.id]['total_value'] += item.current_stock * float(item.local_price)

                if item.current_stock > 0:
                    products_summary[item.id]['stores_with_stock'] += 1

                if item.current_stock <= item.min_stock:
                    products_summary[item.id]['stores_low_stock'] += 1

                products_summary[item.id]['stores_detail'].append({
                    'store_id': item.store_id,
                    'store_name': item.store_name,
                    'store_code': item.store_code,
                    'current_stock': item.current_stock,
                    'min_stock': item.min_stock,
                    'max_stock': item.max_stock,
                    'local_price': float(item.local_price),
                    'stock_value': item.current_stock * float(item.local_price),
                    'stock_status': 'out_of_stock' if item.current_stock == 0 else 'low_stock' if item.current_stock <= item.min_stock else 'healthy',
                    'last_updated': item.updated_at.isoformat() if item.updated_at else None
                })

                # Resumen por tienda
                if item.store_id not in stores_summary:
                    stores_summary[item.store_id] = {
                        'store_id': item.store_id,
                        'store_name': item.store_name,
                        'store_code': item.store_code,
                        'total_products': 0,
                        'products_with_stock': 0,
                        'products_low_stock': 0,
                        'products_out_of_stock': 0,
                        'total_inventory_value': 0
                    }

                stores_summary[item.store_id]['total_products'] += 1
                stores_summary[item.store_id]['total_inventory_value'] += item.current_stock * float(item.local_price)

                if item.current_stock > 0:
                    stores_summary[item.store_id]['products_with_stock'] += 1
                elif item.current_stock == 0:
                    stores_summary[item.store_id]['products_out_of_stock'] += 1

                if item.current_stock <= item.min_stock:
                    stores_summary[item.store_id]['products_low_stock'] += 1

                total_inventory_value += item.current_stock * float(item.local_price)

            # Calcular promedios de precio por producto
            for product_id, product_data in products_summary.items():
                if product_data['stores_count'] > 0:
                    total_price = sum(store['local_price'] for store in product_data['stores_detail'])
                    product_data['average_price'] = round(total_price / product_data['stores_count'], 2)

            # Incluir transferencias si se solicita
            transfers_data = []
            if include_transfers:
                transfers_query = InventoryTransfer.query.filter(
                    InventoryTransfer.status.in_(['pending', 'approved', 'in_transit'])
                )

                if store_ids:
                    transfers_query = transfers_query.filter(
                        or_(
                            InventoryTransfer.from_store_id.in_(store_ids),
                            InventoryTransfer.to_store_id.in_(store_ids)
                        )
                    )

                active_transfers = transfers_query.all()

                transfers_data = [
                    {
                        'transfer_id': transfer.id,
                        'transfer_number': transfer.transfer_number,
                        'from_store': transfer.from_store.name,
                        'to_store': transfer.to_store.name,
                        'status': transfer.status.value,
                        'total_items': transfer.total_items,
                        'created_at': transfer.created_at.isoformat(),
                        'expected_delivery': transfer.expected_delivery.isoformat() if transfer.expected_delivery else None
                    }
                    for transfer in active_transfers
                ]

            return {
                'report_info': {
                    'type': 'inventory_report',
                    'filters': {
                        'store_ids': store_ids,
                        'include_transfers': include_transfers,
                        'low_stock_only': low_stock_only
                    },
                    'generated_at': datetime.utcnow().isoformat()
                },
                'summary': {
                    'total_products': len(products_summary),
                    'total_stores': len(stores_summary),
                    'total_inventory_value': round(total_inventory_value, 2),
                    'products_with_low_stock': sum(1 for p in products_summary.values() if p['stores_low_stock'] > 0),
                    'active_transfers': len(transfers_data)
                },
                'products_summary': list(products_summary.values()),
                'stores_summary': list(stores_summary.values()),
                'active_transfers': transfers_data
            }

        except Exception as e:
            logger.error(f"Error generando reporte de inventario: {e}")
            raise

    def generate_performance_report(self,
                                    start_date: datetime,
                                    end_date: datetime,
                                    store_ids: List[int] = None) -> Dict[str, Any]:
        """Generar reporte de performance multi-sede"""
        try:
            # Obtener datos de ventas por tienda
            sales_query = db.session.query(
                Store.id,
                Store.name,
                Store.code,
                func.count(Sale.id).label('total_sales'),
                func.sum(Sale.total).label('total_revenue'),
                func.avg(Sale.total).label('avg_sale_value'),
                func.count(func.distinct(Sale.user_id)).label('active_users')
            ).join(Sale).filter(
                Sale.created_at >= start_date,
                Sale.created_at <= end_date,
                Store.is_active.is_(True)
            )

            if store_ids:
                sales_query = sales_query.filter(Store.id.in_(store_ids))

            sales_data = sales_query.group_by(Store.id, Store.name, Store.code).all()

            # Calcular métricas de performance
            total_revenue = sum(float(store.total_revenue or 0) for store in sales_data)
            total_sales = sum(store.total_sales for store in sales_data)

            stores_performance = []
            for store in sales_data:
                revenue_share = (float(store.total_revenue or 0) / total_revenue * 100) if total_revenue > 0 else 0
                sales_share = (store.total_sales / total_sales * 100) if total_sales > 0 else 0

                # Calcular ranking de performance (combinando revenue y volumen de ventas)
                performance_score = (revenue_share * 0.7) + (sales_share * 0.3)

                stores_performance.append({
                    'store_id': store.id,
                    'store_name': store.name,
                    'store_code': store.code,
                    'total_sales': store.total_sales,
                    'total_revenue': round(float(store.total_revenue or 0), 2),
                    'average_sale_value': round(float(store.avg_sale_value or 0), 2),
                    'active_users': store.active_users,
                    'revenue_share_percentage': round(revenue_share, 2),
                    'sales_share_percentage': round(sales_share, 2),
                    'performance_score': round(performance_score, 2)
                })

            # Ordenar por performance score
            stores_performance.sort(key=lambda x: x['performance_score'], reverse=True)

            # Agregar ranking
            for i, store in enumerate(stores_performance, 1):
                store['ranking'] = i

            # Identificar top performers y underperformers
            avg_performance = sum(s['performance_score'] for s in stores_performance) / \
                len(stores_performance) if stores_performance else 0

            top_performers = [s for s in stores_performance if s['performance_score'] > avg_performance * 1.2]
            underperformers = [s for s in stores_performance if s['performance_score'] < avg_performance * 0.8]

            return {
                'report_info': {
                    'type': 'performance_report',
                    'period': {
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat()
                    },
                    'filters': {
                        'store_ids': store_ids
                    },
                    'generated_at': datetime.utcnow().isoformat()
                },
                'overall_metrics': {
                    'total_stores_analyzed': len(stores_performance),
                    'total_revenue': round(total_revenue, 2),
                    'total_sales': total_sales,
                    'average_revenue_per_store': round(total_revenue / len(stores_performance), 2) if stores_performance else 0,
                    'average_sales_per_store': round(total_sales / len(stores_performance), 2) if stores_performance else 0
                },
                'stores_performance': stores_performance,
                'insights': {
                    'top_performers': top_performers[:3],  # Top 3
                    'underperformers': underperformers,
                    'average_performance_score': round(avg_performance, 2),
                    'performance_variance': round(max(s['performance_score'] for s in stores_performance) - min(s['performance_score'] for s in stores_performance), 2) if stores_performance else 0
                }
            }

        except Exception as e:
            logger.error(f"Error generando reporte de performance: {e}")
            raise

    def export_report(self, report_data: Dict[str, Any], format_type: str = 'json') -> Any:
        """Exportar reporte en formato especificado"""
        try:
            if format_type not in self.supported_formats:
                raise ValidationError(f"Formato no soportado: {format_type}. Soportados: {self.supported_formats}")

            if format_type == 'json':
                return json.dumps(report_data, indent=2, default=str)

            elif format_type == 'csv':
                # Implementar conversión a CSV (simplificado)
                import csv
                import io

                output = io.StringIO()

                # Determinar tipo de reporte y extraer datos tabulares
                if report_data.get('report_info', {}).get('type') == 'sales_report':
                    writer = csv.writer(output)
                    writer.writerow(['Group', 'Sales Count', 'Revenue', 'Tax', 'Average Sale'])

                    for group in report_data.get('grouped_data', []):
                        writer.writerow([
                            group['group_label'],
                            group['total_sales'],
                            group['total_revenue'],
                            group['total_tax'],
                            group['average_sale']
                        ])

                return output.getvalue()

            elif format_type == 'excel':
                # Placeholder para implementación de Excel
                # En producción, usar openpyxl o xlsxwriter
                return "Excel export not implemented yet"

        except Exception as e:
            logger.error(f"Error exportando reporte: {e}")
            raise

    def schedule_report(self,
                        report_type: str,
                        schedule_config: Dict[str, Any],
                        recipients: List[str]) -> Dict[str, Any]:
        """Programar generación automática de reportes"""
        try:
            # Placeholder para implementación de reportes programados
            # En producción, integrar con Celery o similar para tareas asíncronas

            scheduled_report = {
                'report_id': f"scheduled_{report_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                'report_type': report_type,
                'schedule_config': schedule_config,
                'recipients': recipients,
                'status': 'scheduled',
                'created_at': datetime.utcnow().isoformat(),
                'next_execution': self._calculate_next_execution(schedule_config)
            }

            logger.info(f"Reporte programado creado: {scheduled_report['report_id']}")

            return scheduled_report

        except Exception as e:
            logger.error(f"Error programando reporte: {e}")
            raise

    def _calculate_next_execution(self, schedule_config: Dict[str, Any]) -> str:
        """Calcular próxima ejecución de reporte programado"""
        try:
            frequency = schedule_config.get('frequency', 'daily')

            if frequency == 'daily':
                next_execution = datetime.utcnow() + timedelta(days=1)
            elif frequency == 'weekly':
                next_execution = datetime.utcnow() + timedelta(weeks=1)
            elif frequency == 'monthly':
                next_execution = datetime.utcnow() + timedelta(days=30)
            else:
                next_execution = datetime.utcnow() + timedelta(days=1)

            return next_execution.isoformat()

        except Exception as e:
            logger.warning(f"Error calculando próxima ejecución: {e}")
            return (datetime.utcnow() + timedelta(days=1)).isoformat()
