"""
Store Service - Sistema Multi-Sede Sabrositas
=============================================
Servicio para gestión de tiendas, sincronización y operaciones multi-sede.
"""

from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from app import db
from app.models.store import Store, StoreProduct
from app.models.product import Product
from app.models.user import User
from app.models.inventory_transfer import InventoryTransfer, InventoryTransferItem, TransferStatus
from app.services.product_service import ProductService
from app.exceptions import ValidationError, BusinessLogicError
import logging

logger = logging.getLogger(__name__)

class StoreService:
    """Servicio para gestión de tiendas y operaciones multi-sede"""
    
    def __init__(self):
        self.product_service = ProductService()
    
    def create_store(self, store_data: Dict[str, Any]) -> Store:
        """Crear nueva tienda"""
        try:
            # Validar datos requeridos
            required_fields = ['code', 'name']
            for field in required_fields:
                if not store_data.get(field):
                    raise ValidationError(f"Campo requerido: {field}")
            
            # Verificar código único
            existing_store = Store.query.filter_by(code=store_data['code']).first()
            if existing_store:
                raise ValidationError(f"Ya existe una tienda con código: {store_data['code']}")
            
            # Crear tienda
            store = Store(
                code=store_data['code'],
                name=store_data['name'],
                address=store_data.get('address'),
                phone=store_data.get('phone'),
                email=store_data.get('email'),
                manager_id=store_data.get('manager_id'),
                region=store_data.get('region'),
                store_type=store_data.get('store_type', 'retail'),
                timezone=store_data.get('timezone', 'America/Bogota'),
                tax_rate=store_data.get('tax_rate', 0.19),
                currency=store_data.get('currency', 'COP')
            )
            
            db.session.add(store)
            db.session.commit()
            
            logger.info(f"Tienda creada: {store.code} - {store.name}")
            return store
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creando tienda: {str(e)}")
            raise
    
    def get_all_stores(self, include_inactive: bool = False) -> List[Store]:
        """Obtener todas las tiendas"""
        query = Store.query
        if not include_inactive:
            query = query.filter_by(is_active=True)
        
        return query.order_by(Store.name).all()
    
    def get_store_by_id(self, store_id: int) -> Optional[Store]:
        """Obtener tienda por ID"""
        return Store.query.get(store_id)
    
    def get_store_by_code(self, code: str) -> Optional[Store]:
        """Obtener tienda por código"""
        return Store.query.filter_by(code=code).first()
    
    def update_store(self, store_id: int, update_data: Dict[str, Any]) -> Store:
        """Actualizar tienda"""
        try:
            store = self.get_store_by_id(store_id)
            if not store:
                raise ValidationError(f"Tienda no encontrada: {store_id}")
            
            # Campos actualizables
            updatable_fields = [
                'name', 'address', 'phone', 'email', 'manager_id', 'region',
                'store_type', 'timezone', 'tax_rate', 'currency', 'is_active',
                'max_concurrent_sales', 'auto_sync_inventory', 'sync_frequency_minutes'
            ]
            
            for field in updatable_fields:
                if field in update_data:
                    setattr(store, field, update_data[field])
            
            store.updated_at = datetime.utcnow()
            db.session.commit()
            
            logger.info(f"Tienda actualizada: {store.code}")
            return store
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error actualizando tienda {store_id}: {str(e)}")
            raise
    
    def assign_products_to_store(self, store_id: int, product_assignments: List[Dict]) -> bool:
        """Asignar productos a una tienda con precios y stock locales"""
        try:
            store = self.get_store_by_id(store_id)
            if not store:
                raise ValidationError(f"Tienda no encontrada: {store_id}")
            
            for assignment in product_assignments:
                product_id = assignment.get('product_id')
                local_price = assignment.get('local_price')
                initial_stock = assignment.get('initial_stock', 0)
                min_stock = assignment.get('min_stock', 5)
                max_stock = assignment.get('max_stock', 100)
                
                # Validar producto existe
                product = Product.query.get(product_id)
                if not product:
                    logger.warning(f"Producto no encontrado: {product_id}")
                    continue
                
                # Verificar si ya existe la relación
                store_product = StoreProduct.query.filter_by(
                    store_id=store_id,
                    product_id=product_id
                ).first()
                
                if store_product:
                    # Actualizar existente
                    store_product.local_price = local_price or product.price
                    store_product.current_stock = initial_stock
                    store_product.min_stock = min_stock
                    store_product.max_stock = max_stock
                    store_product.updated_at = datetime.utcnow()
                else:
                    # Crear nueva relación
                    store_product = StoreProduct(
                        store_id=store_id,
                        product_id=product_id,
                        local_price=local_price or product.price,
                        cost_price=product.cost,
                        current_stock=initial_stock,
                        min_stock=min_stock,
                        max_stock=max_stock
                    )
                    db.session.add(store_product)
            
            db.session.commit()
            logger.info(f"Productos asignados a tienda {store.code}: {len(product_assignments)}")
            return True
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error asignando productos a tienda {store_id}: {str(e)}")
            raise
    
    def sync_all_products_to_store(self, store_id: int) -> bool:
        """Sincronizar todos los productos activos a una tienda"""
        try:
            store = self.get_store_by_id(store_id)
            if not store:
                raise ValidationError(f"Tienda no encontrada: {store_id}")
            
            # Obtener todos los productos activos
            active_products = Product.query.filter_by(is_active=True).all()
            
            assignments = []
            for product in active_products:
                assignments.append({
                    'product_id': product.id,
                    'local_price': float(product.price),
                    'initial_stock': 0,  # Stock inicial en 0
                    'min_stock': product.min_stock,
                    'max_stock': product.max_stock or 100
                })
            
            return self.assign_products_to_store(store_id, assignments)
            
        except Exception as e:
            logger.error(f"Error sincronizando productos a tienda {store_id}: {str(e)}")
            raise
    
    def get_store_inventory(self, store_id: int, include_inactive: bool = False) -> List[Dict]:
        """Obtener inventario completo de una tienda"""
        try:
            query = db.session.query(StoreProduct, Product).join(Product).filter(
                StoreProduct.store_id == store_id
            )
            
            if not include_inactive:
                query = query.filter(Product.is_active == True, StoreProduct.is_available == True)
            
            results = query.order_by(Product.name).all()
            
            inventory = []
            for store_product, product in results:
                inventory.append({
                    'product_id': product.id,
                    'product_name': product.name,
                    'sku': product.sku,
                    'category': product.category,
                    'local_price': float(store_product.local_price),
                    'cost_price': float(store_product.cost_price) if store_product.cost_price else None,
                    'current_stock': store_product.current_stock,
                    'min_stock': store_product.min_stock,
                    'max_stock': store_product.max_stock,
                    'is_low_stock': store_product.is_low_stock,
                    'is_out_of_stock': store_product.is_out_of_stock,
                    'profit_margin': store_product.profit_margin,
                    'is_available': store_product.is_available,
                    'last_sale_at': store_product.last_sale_at.isoformat() if store_product.last_sale_at else None
                })
            
            return inventory
            
        except Exception as e:
            logger.error(f"Error obteniendo inventario de tienda {store_id}: {str(e)}")
            raise
    
    def get_low_stock_products(self, store_id: int = None) -> List[Dict]:
        """Obtener productos con stock bajo"""
        try:
            query = db.session.query(StoreProduct, Product, Store).join(Product).join(Store).filter(
                StoreProduct.current_stock <= StoreProduct.min_stock,
                StoreProduct.is_available == True,
                Product.is_active == True,
                Store.is_active == True
            )
            
            if store_id:
                query = query.filter(StoreProduct.store_id == store_id)
            
            results = query.order_by(Store.name, Product.name).all()
            
            low_stock = []
            for store_product, product, store in results:
                low_stock.append({
                    'store_id': store.id,
                    'store_name': store.name,
                    'store_code': store.code,
                    'product_id': product.id,
                    'product_name': product.name,
                    'sku': product.sku,
                    'current_stock': store_product.current_stock,
                    'min_stock': store_product.min_stock,
                    'reorder_point': store_product.reorder_point,
                    'suggested_order': store_product.max_stock - store_product.current_stock
                })
            
            return low_stock
            
        except Exception as e:
            logger.error(f"Error obteniendo productos con stock bajo: {str(e)}")
            raise
    
    def create_transfer(self, transfer_data: Dict[str, Any]) -> InventoryTransfer:
        """Crear transferencia de inventario entre tiendas"""
        try:
            # Validar datos requeridos
            required_fields = ['from_store_id', 'to_store_id', 'requested_by', 'items']
            for field in required_fields:
                if not transfer_data.get(field):
                    raise ValidationError(f"Campo requerido: {field}")
            
            # Validar tiendas existen
            from_store = self.get_store_by_id(transfer_data['from_store_id'])
            to_store = self.get_store_by_id(transfer_data['to_store_id'])
            
            if not from_store or not to_store:
                raise ValidationError("Tienda origen o destino no encontrada")
            
            if from_store.id == to_store.id:
                raise ValidationError("No se puede transferir a la misma tienda")
            
            # Crear transferencia
            transfer = InventoryTransfer(
                from_store_id=transfer_data['from_store_id'],
                to_store_id=transfer_data['to_store_id'],
                requested_by=transfer_data['requested_by'],
                reason=transfer_data.get('reason', ''),
                notes=transfer_data.get('notes', ''),
                priority=transfer_data.get('priority', 'normal'),
                transfer_type=transfer_data.get('transfer_type', 'manual'),
                expected_delivery=transfer_data.get('expected_delivery')
            )
            
            # Generar número de transferencia
            transfer.transfer_number = transfer.generate_transfer_number()
            
            db.session.add(transfer)
            db.session.flush()  # Para obtener el ID
            
            # Agregar items
            total_cost = 0
            total_items = 0
            
            for item_data in transfer_data['items']:
                product_id = item_data.get('product_id')
                quantity = item_data.get('quantity', 0)
                
                if quantity <= 0:
                    continue
                
                # Obtener precio de costo del producto en tienda origen
                store_product = StoreProduct.query.filter_by(
                    store_id=transfer_data['from_store_id'],
                    product_id=product_id
                ).first()
                
                if not store_product:
                    logger.warning(f"Producto {product_id} no encontrado en tienda origen")
                    continue
                
                # Verificar stock disponible
                if store_product.current_stock < quantity:
                    raise BusinessLogicError(
                        f"Stock insuficiente para producto {product_id}. "
                        f"Disponible: {store_product.current_stock}, Solicitado: {quantity}"
                    )
                
                unit_cost = store_product.cost_price or store_product.local_price
                item_total = float(unit_cost) * quantity
                
                transfer_item = InventoryTransferItem(
                    transfer_id=transfer.id,
                    product_id=product_id,
                    quantity=quantity,
                    unit_cost=unit_cost,
                    total_cost=item_total,
                    notes=item_data.get('notes', '')
                )
                
                db.session.add(transfer_item)
                total_cost += item_total
                total_items += quantity
            
            # Actualizar totales
            transfer.total_items = total_items
            transfer.total_cost = total_cost
            
            db.session.commit()
            
            logger.info(f"Transferencia creada: {transfer.transfer_number}")
            return transfer
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creando transferencia: {str(e)}")
            raise
    
    def get_store_transfers(self, store_id: int, status: str = None) -> List[InventoryTransfer]:
        """Obtener transferencias de una tienda"""
        try:
            query = InventoryTransfer.query.filter(
                (InventoryTransfer.from_store_id == store_id) |
                (InventoryTransfer.to_store_id == store_id)
            )
            
            if status:
                query = query.filter(InventoryTransfer.status == status)
            
            return query.order_by(InventoryTransfer.created_at.desc()).all()
            
        except Exception as e:
            logger.error(f"Error obteniendo transferencias de tienda {store_id}: {str(e)}")
            raise
    
    def get_consolidated_inventory(self) -> List[Dict]:
        """Obtener inventario consolidado de todas las tiendas"""
        try:
            query = db.session.query(
                Product.id,
                Product.name,
                Product.sku,
                Product.category,
                db.func.sum(StoreProduct.current_stock).label('total_stock'),
                db.func.count(StoreProduct.store_id).label('stores_count'),
                db.func.avg(StoreProduct.local_price).label('avg_price'),
                db.func.sum(
                    db.case([(StoreProduct.current_stock <= StoreProduct.min_stock, 1)], else_=0)
                ).label('low_stock_stores')
            ).join(StoreProduct).join(Store).filter(
                Product.is_active == True,
                StoreProduct.is_available == True,
                Store.is_active == True
            ).group_by(Product.id, Product.name, Product.sku, Product.category).order_by(Product.name)
            
            results = query.all()
            
            consolidated = []
            for result in results:
                consolidated.append({
                    'product_id': result.id,
                    'product_name': result.name,
                    'sku': result.sku,
                    'category': result.category,
                    'total_stock': int(result.total_stock) if result.total_stock else 0,
                    'stores_count': int(result.stores_count),
                    'average_price': float(result.avg_price) if result.avg_price else 0,
                    'low_stock_stores': int(result.low_stock_stores) if result.low_stock_stores else 0
                })
            
            return consolidated
            
        except Exception as e:
            logger.error(f"Error obteniendo inventario consolidado: {str(e)}")
            raise
    
    def get_store_performance_metrics(self, store_id: int, days: int = 30) -> Dict[str, Any]:
        """Obtener métricas de desempeño de una tienda"""
        try:
            store = self.get_store_by_id(store_id)
            if not store:
                raise ValidationError(f"Tienda no encontrada: {store_id}")
            
            # Fecha de inicio para métricas
            start_date = datetime.utcnow() - timedelta(days=days)
            
            # Métricas básicas
            total_products = len([sp for sp in store.store_products if sp.is_available])
            low_stock_products = len([sp for sp in store.store_products if sp.is_low_stock])
            out_of_stock_products = len([sp for sp in store.store_products if sp.is_out_of_stock])
            
            # Calcular valor total del inventario
            total_inventory_value = sum(
                sp.current_stock * sp.local_price 
                for sp in store.store_products 
                if sp.is_available
            )
            
            metrics = {
                'store_info': store.to_dict(),
                'inventory_metrics': {
                    'total_products': total_products,
                    'low_stock_products': low_stock_products,
                    'out_of_stock_products': out_of_stock_products,
                    'stock_health_percentage': ((total_products - low_stock_products) / total_products * 100) if total_products > 0 else 0,
                    'total_inventory_value': float(total_inventory_value)
                },
                'sync_status': {
                    'is_online': store.is_online,
                    'last_sync': store.last_sync_at.isoformat() if store.last_sync_at else None,
                    'auto_sync_enabled': store.auto_sync_inventory,
                    'sync_frequency_minutes': store.sync_frequency_minutes
                }
            }
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error obteniendo métricas de tienda {store_id}: {str(e)}")
            raise
    
    def update_store_sync_status(self, store_id: int) -> bool:
        """Actualizar estado de sincronización de una tienda"""
        try:
            store = self.get_store_by_id(store_id)
            if not store:
                return False
            
            store.update_sync_timestamp()
            logger.info(f"Sincronización actualizada para tienda: {store.code}")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando sincronización de tienda {store_id}: {str(e)}")
            return False
