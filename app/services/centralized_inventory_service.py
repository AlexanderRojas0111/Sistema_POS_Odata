"""
Centralized Inventory Service - Sistema Multi-Sede Sabrositas
============================================================
Servicio para gestión centralizada de inventario multi-tienda.
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from app import db
from app.models.store import Store, StoreProduct
from app.models.product import Product
from app.models.inventory_transfer import InventoryTransfer, InventoryTransferItem, TransferStatus
from app.services.store_service import StoreService
from app.services.sync_service import SyncService
from app.exceptions import ValidationError, BusinessLogicError
from sqlalchemy import func, and_, or_

logger = logging.getLogger(__name__)

class CentralizedInventoryService:
    """Servicio de gestión centralizada de inventario"""
    
    def __init__(self):
        self.store_service = StoreService()
        self.sync_service = SyncService()
    
    def get_global_inventory_summary(self) -> Dict[str, Any]:
        """Obtener resumen global de inventario"""
        try:
            # Estadísticas generales
            total_products = Product.query.filter_by(is_active=True).count()
            active_stores = Store.query.filter_by(is_active=True).count()
            
            # Valor total del inventario
            total_inventory_value = db.session.query(
                func.sum(StoreProduct.current_stock * StoreProduct.local_price)
            ).join(Store).filter(
                Store.is_active == True,
                StoreProduct.is_available == True
            ).scalar() or 0
            
            # Productos con stock crítico
            critical_stock_count = db.session.query(
                func.count(StoreProduct.product_id.distinct())
            ).filter(
                StoreProduct.current_stock <= StoreProduct.min_stock,
                StoreProduct.is_available == True
            ).scalar() or 0
            
            # Productos agotados
            out_of_stock_count = db.session.query(
                func.count(StoreProduct.product_id.distinct())
            ).filter(
                StoreProduct.current_stock == 0,
                StoreProduct.is_available == True
            ).scalar() or 0
            
            # Transferencias activas
            active_transfers = InventoryTransfer.query.filter(
                InventoryTransfer.status.in_([TransferStatus.PENDING, TransferStatus.APPROVED, TransferStatus.IN_TRANSIT])
            ).count()
            
            # Productos más vendidos (último mes)
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            top_products = db.session.query(
                Product.name,
                func.sum(StoreProduct.current_stock).label('total_stock'),
                func.count(StoreProduct.store_id).label('stores_count')
            ).join(StoreProduct).join(Store).filter(
                Store.is_active == True,
                StoreProduct.is_available == True,
                Product.is_active == True
            ).group_by(Product.id, Product.name).order_by(
                func.sum(StoreProduct.current_stock).desc()
            ).limit(10).all()
            
            return {
                'summary': {
                    'total_products': total_products,
                    'active_stores': active_stores,
                    'total_inventory_value': float(total_inventory_value),
                    'critical_stock_products': critical_stock_count,
                    'out_of_stock_products': out_of_stock_count,
                    'active_transfers': active_transfers,
                    'inventory_health_score': self._calculate_inventory_health_score()
                },
                'top_products_by_stock': [
                    {
                        'product_name': product.name,
                        'total_stock': int(product.total_stock),
                        'stores_count': int(product.stores_count)
                    }
                    for product in top_products
                ],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo resumen global de inventario: {e}")
            raise
    
    def _calculate_inventory_health_score(self) -> float:
        """Calcular score de salud del inventario (0-100)"""
        try:
            # Total de productos activos en tiendas
            total_products = db.session.query(
                func.count(StoreProduct.product_id)
            ).join(Store).filter(
                Store.is_active == True,
                StoreProduct.is_available == True
            ).scalar() or 1
            
            # Productos con stock adecuado
            healthy_products = db.session.query(
                func.count(StoreProduct.product_id)
            ).join(Store).filter(
                Store.is_active == True,
                StoreProduct.is_available == True,
                StoreProduct.current_stock > StoreProduct.min_stock
            ).scalar() or 0
            
            # Calcular porcentaje de salud
            health_score = (healthy_products / total_products) * 100
            return round(health_score, 2)
            
        except Exception as e:
            logger.warning(f"Error calculando score de salud: {e}")
            return 0.0
    
    def get_product_distribution(self, product_id: int) -> Dict[str, Any]:
        """Obtener distribución de un producto en todas las tiendas"""
        try:
            product = Product.query.get(product_id)
            if not product:
                raise ValidationError(f"Producto no encontrado: {product_id}")
            
            # Obtener distribución por tienda
            distribution = db.session.query(
                Store.id,
                Store.name,
                Store.code,
                Store.region,
                StoreProduct.current_stock,
                StoreProduct.min_stock,
                StoreProduct.max_stock,
                StoreProduct.local_price,
                StoreProduct.is_available,
                StoreProduct.last_sale_at
            ).join(StoreProduct).filter(
                StoreProduct.product_id == product_id,
                Store.is_active == True
            ).order_by(Store.name).all()
            
            # Calcular estadísticas
            total_stock = sum(d.current_stock for d in distribution)
            avg_price = sum(d.local_price for d in distribution) / len(distribution) if distribution else 0
            stores_with_stock = sum(1 for d in distribution if d.current_stock > 0)
            stores_low_stock = sum(1 for d in distribution if d.current_stock <= d.min_stock)
            
            return {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'sku': product.sku,
                    'category': product.category
                },
                'distribution': [
                    {
                        'store_id': d.id,
                        'store_name': d.name,
                        'store_code': d.code,
                        'region': d.region,
                        'current_stock': d.current_stock,
                        'min_stock': d.min_stock,
                        'max_stock': d.max_stock,
                        'local_price': float(d.local_price),
                        'is_available': d.is_available,
                        'stock_status': self._get_stock_status(d.current_stock, d.min_stock),
                        'last_sale_at': d.last_sale_at.isoformat() if d.last_sale_at else None
                    }
                    for d in distribution
                ],
                'statistics': {
                    'total_stock': total_stock,
                    'average_price': float(avg_price),
                    'stores_with_stock': stores_with_stock,
                    'stores_low_stock': stores_low_stock,
                    'total_stores': len(distribution)
                }
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo distribución del producto {product_id}: {e}")
            raise
    
    def _get_stock_status(self, current_stock: int, min_stock: int) -> str:
        """Determinar estado del stock"""
        if current_stock == 0:
            return 'out_of_stock'
        elif current_stock <= min_stock:
            return 'low_stock'
        else:
            return 'healthy'
    
    def suggest_inventory_rebalancing(self) -> List[Dict[str, Any]]:
        """Sugerir rebalanceo de inventario entre tiendas"""
        try:
            suggestions = []
            
            # Obtener productos con desbalance
            products_query = db.session.query(
                Product.id,
                Product.name,
                func.sum(StoreProduct.current_stock).label('total_stock'),
                func.avg(StoreProduct.current_stock).label('avg_stock'),
                func.max(StoreProduct.current_stock).label('max_stock'),
                func.min(StoreProduct.current_stock).label('min_stock'),
                func.count(StoreProduct.store_id).label('stores_count')
            ).join(StoreProduct).join(Store).filter(
                Store.is_active == True,
                StoreProduct.is_available == True,
                Product.is_active == True
            ).group_by(Product.id, Product.name).having(
                func.max(StoreProduct.current_stock) > func.min(StoreProduct.current_stock) * 3
            ).all()
            
            for product in products_query:
                # Obtener tiendas con exceso y déficit
                stores_data = db.session.query(
                    Store.id,
                    Store.name,
                    Store.code,
                    StoreProduct.current_stock,
                    StoreProduct.min_stock,
                    StoreProduct.max_stock
                ).join(StoreProduct).filter(
                    StoreProduct.product_id == product.id,
                    Store.is_active == True
                ).all()
                
                # Identificar tiendas con exceso (stock > promedio * 1.5)
                excess_stores = [
                    s for s in stores_data 
                    if s.current_stock > product.avg_stock * 1.5 and s.current_stock > s.min_stock * 2
                ]
                
                # Identificar tiendas con déficit (stock < min_stock)
                deficit_stores = [
                    s for s in stores_data 
                    if s.current_stock <= s.min_stock
                ]
                
                if excess_stores and deficit_stores:
                    # Calcular transferencias sugeridas
                    for deficit_store in deficit_stores:
                        needed_quantity = deficit_store.max_stock - deficit_store.current_stock
                        
                        # Buscar mejor tienda donante
                        best_donor = max(
                            excess_stores,
                            key=lambda s: s.current_stock - s.min_stock,
                            default=None
                        )
                        
                        if best_donor:
                            available_quantity = best_donor.current_stock - best_donor.min_stock
                            transfer_quantity = min(needed_quantity, available_quantity, needed_quantity)
                            
                            if transfer_quantity > 0:
                                suggestions.append({
                                    'product_id': product.id,
                                    'product_name': product.name,
                                    'from_store_id': best_donor.id,
                                    'from_store_name': best_donor.name,
                                    'from_store_current_stock': best_donor.current_stock,
                                    'to_store_id': deficit_store.id,
                                    'to_store_name': deficit_store.name,
                                    'to_store_current_stock': deficit_store.current_stock,
                                    'suggested_quantity': transfer_quantity,
                                    'priority': self._calculate_transfer_priority(
                                        deficit_store.current_stock,
                                        deficit_store.min_stock,
                                        product.avg_stock
                                    ),
                                    'estimated_cost': float(transfer_quantity * 5.0)  # Costo estimado de transferencia
                                })
            
            # Ordenar por prioridad
            suggestions.sort(key=lambda x: x['priority'], reverse=True)
            
            return suggestions[:20]  # Top 20 sugerencias
            
        except Exception as e:
            logger.error(f"Error generando sugerencias de rebalanceo: {e}")
            raise
    
    def _calculate_transfer_priority(self, current_stock: int, min_stock: int, avg_stock: float) -> int:
        """Calcular prioridad de transferencia (1-10)"""
        if current_stock == 0:
            return 10  # Máxima prioridad
        elif current_stock < min_stock * 0.5:
            return 9
        elif current_stock <= min_stock:
            return 7
        elif current_stock < avg_stock * 0.7:
            return 5
        else:
            return 3
    
    def create_automatic_transfer(self, suggestion: Dict[str, Any], requested_by: int) -> Optional[InventoryTransfer]:
        """Crear transferencia automática basada en sugerencia"""
        try:
            transfer_data = {
                'from_store_id': suggestion['from_store_id'],
                'to_store_id': suggestion['to_store_id'],
                'requested_by': requested_by,
                'reason': f"Rebalanceo automático - Producto: {suggestion['product_name']}",
                'transfer_type': 'automatic',
                'priority': 'high' if suggestion['priority'] >= 8 else 'normal',
                'items': [
                    {
                        'product_id': suggestion['product_id'],
                        'quantity': suggestion['suggested_quantity']
                    }
                ]
            }
            
            transfer = self.store_service.create_transfer(transfer_data)
            
            # Auto-aprobar transferencias de baja cantidad
            if suggestion['suggested_quantity'] <= 10:
                transfer.approve_transfer(requested_by)
                db.session.commit()
            
            logger.info(f"Transferencia automática creada: {transfer.transfer_number}")
            return transfer
            
        except Exception as e:
            logger.error(f"Error creando transferencia automática: {e}")
            return None
    
    def get_inventory_alerts(self, severity: str = None) -> List[Dict[str, Any]]:
        """Obtener alertas de inventario"""
        try:
            alerts = []
            
            # Alertas de stock crítico
            critical_products = db.session.query(
                Product.id,
                Product.name,
                Store.id.label('store_id'),
                Store.name.label('store_name'),
                StoreProduct.current_stock,
                StoreProduct.min_stock
            ).join(StoreProduct).join(Store).filter(
                StoreProduct.current_stock <= StoreProduct.min_stock,
                StoreProduct.current_stock > 0,
                Store.is_active == True,
                StoreProduct.is_available == True
            ).all()
            
            for product in critical_products:
                alerts.append({
                    'type': 'critical_stock',
                    'severity': 'high',
                    'product_id': product.id,
                    'product_name': product.name,
                    'store_id': product.store_id,
                    'store_name': product.store_name,
                    'current_stock': product.current_stock,
                    'min_stock': product.min_stock,
                    'message': f"Stock crítico: {product.name} en {product.store_name} ({product.current_stock} unidades)",
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Alertas de productos agotados
            out_of_stock = db.session.query(
                Product.id,
                Product.name,
                Store.id.label('store_id'),
                Store.name.label('store_name')
            ).join(StoreProduct).join(Store).filter(
                StoreProduct.current_stock == 0,
                Store.is_active == True,
                StoreProduct.is_available == True
            ).all()
            
            for product in out_of_stock:
                alerts.append({
                    'type': 'out_of_stock',
                    'severity': 'medium',
                    'product_id': product.id,
                    'product_name': product.name,
                    'store_id': product.store_id,
                    'store_name': product.store_name,
                    'message': f"Producto agotado: {product.name} en {product.store_name}",
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Alertas de transferencias vencidas
            overdue_transfers = InventoryTransfer.query.filter(
                InventoryTransfer.expected_delivery < datetime.utcnow(),
                InventoryTransfer.status.in_([TransferStatus.APPROVED, TransferStatus.IN_TRANSIT])
            ).all()
            
            for transfer in overdue_transfers:
                hours_overdue = (datetime.utcnow() - transfer.expected_delivery).total_seconds() / 3600
                alerts.append({
                    'type': 'transfer_overdue',
                    'severity': 'high' if hours_overdue > 48 else 'medium',
                    'transfer_id': transfer.id,
                    'transfer_number': transfer.transfer_number,
                    'from_store': transfer.from_store.name,
                    'to_store': transfer.to_store.name,
                    'hours_overdue': round(hours_overdue, 1),
                    'message': f"Transferencia vencida: {transfer.transfer_number} ({round(hours_overdue, 1)}h de retraso)",
                    'timestamp': datetime.utcnow().isoformat()
                })
            
            # Filtrar por severidad si se especifica
            if severity:
                alerts = [alert for alert in alerts if alert['severity'] == severity]
            
            # Ordenar por severidad y timestamp
            severity_order = {'high': 3, 'medium': 2, 'low': 1}
            alerts.sort(key=lambda x: (severity_order.get(x['severity'], 0), x['timestamp']), reverse=True)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error obteniendo alertas de inventario: {e}")
            raise
    
    def execute_inventory_reconciliation(self, store_id: int = None) -> Dict[str, Any]:
        """Ejecutar reconciliación de inventario"""
        try:
            reconciliation_results = {
                'stores_processed': 0,
                'products_reconciled': 0,
                'discrepancies_found': 0,
                'corrections_applied': 0,
                'errors': [],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Determinar tiendas a procesar
            if store_id:
                stores = [Store.query.get(store_id)]
                if not stores[0]:
                    raise ValidationError(f"Tienda no encontrada: {store_id}")
            else:
                stores = Store.query.filter_by(is_active=True).all()
            
            for store in stores:
                try:
                    store_results = self._reconcile_store_inventory(store.id)
                    reconciliation_results['stores_processed'] += 1
                    reconciliation_results['products_reconciled'] += store_results['products_processed']
                    reconciliation_results['discrepancies_found'] += store_results['discrepancies']
                    reconciliation_results['corrections_applied'] += store_results['corrections']
                    
                except Exception as e:
                    error_msg = f"Error reconciliando tienda {store.name}: {e}"
                    reconciliation_results['errors'].append(error_msg)
                    logger.error(error_msg)
            
            return reconciliation_results
            
        except Exception as e:
            logger.error(f"Error ejecutando reconciliación de inventario: {e}")
            raise
    
    def _reconcile_store_inventory(self, store_id: int) -> Dict[str, int]:
        """Reconciliar inventario de una tienda específica"""
        try:
            results = {
                'products_processed': 0,
                'discrepancies': 0,
                'corrections': 0
            }
            
            # Obtener productos de la tienda
            store_products = StoreProduct.query.filter_by(
                store_id=store_id,
                is_available=True
            ).all()
            
            for store_product in store_products:
                results['products_processed'] += 1
                
                # Verificar consistencia de datos
                discrepancy_found = False
                
                # Verificar stock negativo no permitido
                if store_product.current_stock < 0 and not store_product.allow_negative_stock:
                    logger.warning(f"Stock negativo detectado: Producto {store_product.product_id}, Tienda {store_id}")
                    store_product.current_stock = 0
                    discrepancy_found = True
                
                # Verificar min_stock > max_stock
                if store_product.min_stock > store_product.max_stock:
                    logger.warning(f"min_stock > max_stock: Producto {store_product.product_id}, Tienda {store_id}")
                    store_product.max_stock = store_product.min_stock * 2
                    discrepancy_found = True
                
                # Verificar precios negativos
                if store_product.local_price <= 0:
                    # Usar precio del producto base
                    base_product = Product.query.get(store_product.product_id)
                    if base_product and base_product.price > 0:
                        store_product.local_price = base_product.price
                        discrepancy_found = True
                
                if discrepancy_found:
                    results['discrepancies'] += 1
                    store_product.updated_at = datetime.utcnow()
                    results['corrections'] += 1
            
            # Commit cambios si hay correcciones
            if results['corrections'] > 0:
                db.session.commit()
                logger.info(f"Reconciliación completada para tienda {store_id}: {results['corrections']} correcciones")
            
            return results
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error reconciliando inventario de tienda {store_id}: {e}")
            raise
    
    def get_inventory_trends(self, days: int = 30) -> Dict[str, Any]:
        """Obtener tendencias de inventario"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Tendencias por tienda
            store_trends = db.session.query(
                Store.id,
                Store.name,
                func.avg(StoreProduct.current_stock).label('avg_stock'),
                func.sum(StoreProduct.current_stock * StoreProduct.local_price).label('inventory_value')
            ).join(StoreProduct).filter(
                Store.is_active == True,
                StoreProduct.is_available == True
            ).group_by(Store.id, Store.name).all()
            
            # Productos con mayor rotación (simulado - en producción usar datos de ventas)
            high_rotation_products = db.session.query(
                Product.id,
                Product.name,
                Product.category,
                func.sum(StoreProduct.current_stock).label('total_stock'),
                func.count(StoreProduct.store_id).label('stores_count')
            ).join(StoreProduct).join(Store).filter(
                Store.is_active == True,
                StoreProduct.is_available == True,
                Product.is_active == True
            ).group_by(Product.id, Product.name, Product.category).order_by(
                func.sum(StoreProduct.current_stock).desc()
            ).limit(10).all()
            
            return {
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                },
                'store_trends': [
                    {
                        'store_id': trend.id,
                        'store_name': trend.name,
                        'average_stock': float(trend.avg_stock or 0),
                        'inventory_value': float(trend.inventory_value or 0)
                    }
                    for trend in store_trends
                ],
                'high_rotation_products': [
                    {
                        'product_id': product.id,
                        'product_name': product.name,
                        'category': product.category,
                        'total_stock': int(product.total_stock),
                        'stores_count': int(product.stores_count)
                    }
                    for product in high_rotation_products
                ],
                'summary': {
                    'total_stores_analyzed': len(store_trends),
                    'total_inventory_value': sum(float(t.inventory_value or 0) for t in store_trends),
                    'average_stock_per_store': sum(float(t.avg_stock or 0) for t in store_trends) / len(store_trends) if store_trends else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo tendencias de inventario: {e}")
            raise
