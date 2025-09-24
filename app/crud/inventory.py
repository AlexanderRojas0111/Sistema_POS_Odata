from app.models import Inventory, Product
from app.core.database import db
from app.schemas import InventoryCreate, InventoryUpdate
from typing import List, Optional

class InventoryCRUD:
    """Clase para operaciones CRUD de inventario"""
    
    def get_all(self, page: int = 1, per_page: int = 20) -> List[Inventory]:
        """Obtener todo el inventario con paginación"""
        return Inventory.query.paginate(
            page=page, per_page=per_page, error_out=False
        ).items
    
    def get(self, inventory_id: int) -> Optional[Inventory]:
        """Obtener un item específico del inventario"""
        return Inventory.query.get(inventory_id)
    
    def create(self, inventory_data: InventoryCreate) -> Inventory:
        """Crear un nuevo item en el inventario"""
        inventory = Inventory(
            product_id=inventory_data.product_id,
            quantity=inventory_data.quantity,
            movement_type=inventory_data.movement_type,
            user_id=inventory_data.user_id
        )
        
        # Actualizar stock del producto
        product = Product.query.get(inventory.product_id)
        if product:
            if inventory.movement_type.lower() == 'compra':
                product.stock += inventory.quantity
            elif inventory.movement_type.lower() == 'devolucion':
                product.stock += inventory.quantity
            elif inventory.movement_type.lower() == 'venta':
                product.stock = max(0, product.stock - inventory.quantity)
            elif inventory.movement_type.lower() == 'ajuste-negativo':
                product.stock = max(0, product.stock - inventory.quantity)
        
        db.session.add(inventory)
        return inventory
    
    def update(self, inventory_id: int, inventory_data: InventoryUpdate) -> Optional[Inventory]:
        """Actualizar un item del inventario"""
        inventory = self.get(inventory_id)
        if not inventory:
            return None
        
        if inventory_data.quantity is not None:
            inventory.quantity = inventory_data.quantity
        if inventory_data.movement_type is not None:
            inventory.movement_type = inventory_data.movement_type
        
        return inventory
    
    def delete(self, inventory_id: int) -> bool:
        """Eliminar un item del inventario"""
        inventory = self.get(inventory_id)
        if not inventory:
            return False
        
        db.session.delete(inventory)
        return True
    
    def get_low_stock(self, threshold: int = 10) -> List[Inventory]:
        """Obtener items con stock bajo"""
        return Inventory.query.join(Product).filter(
            Product.stock <= threshold
        ).all()

# Instancia global del CRUD
inventory_crud = InventoryCRUD() 