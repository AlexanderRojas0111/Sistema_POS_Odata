from typing import Dict, Any
from .base_agent import BaseAgent
from app.models import Product, Inventory
from app.core.database import db
from app.rag.embeddings import EmbeddingService

class InventoryAgent(BaseAgent):
    def __init__(self, low_stock_threshold: int = 5):
        super().__init__(name="InventoryAgent")
        self.low_stock_threshold = low_stock_threshold
        self.embedding_service = EmbeddingService()
        
    async def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Procesa mensajes relacionados con el inventario"""
        action = message.get('action')
        if action == 'check_stock':
            return await self.check_stock(message.get('product_id'))
        elif action == 'update_stock':
            return await self.update_stock(
                message.get('product_id'),
                message.get('quantity'),
                message.get('movement_type')
            )
        elif action == 'find_similar':
            return await self.find_similar_products(message.get('query'))
            
        return {'error': 'Acción no soportada'}
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Ejecuta tareas programadas del inventario"""
        task_type = task.get('type')
        if task_type == 'check_low_stock':
            return await self.check_low_stock_products()
        elif task_type == 'generate_embeddings':
            return await self.generate_product_embeddings()
            
        return {'error': 'Tipo de tarea no soportada'}
    
    async def check_stock(self, product_id: int) -> Dict[str, Any]:
        """Verifica el stock de un producto"""
        product = Product.query.get(product_id)
        if not product:
            return {'error': 'Producto no encontrado'}
            
        return {
            'product_id': product_id,
            'current_stock': product.stock,
            'low_stock_alert': product.stock <= self.low_stock_threshold
        }
    
    async def update_stock(self, product_id: int, quantity: int, movement_type: str) -> Dict[str, Any]:
        """Actualiza el stock de un producto"""
        product = Product.query.get(product_id)
        if not product:
            return {'error': 'Producto no encontrado'}
            
        product.stock += quantity
        
        inventory_movement = Inventory(
            product_id=product_id,
            quantity=quantity,
            movement_type=movement_type,
            user_id=1  # TODO: Implementar sistema de usuarios para agentes
        )
        
        db.session.add(inventory_movement)
        db.session.commit()
        
        return {
            'product_id': product_id,
            'new_stock': product.stock,
            'movement': {
                'quantity': quantity,
                'type': movement_type
            }
        }
    
    async def check_low_stock_products(self) -> Dict[str, Any]:
        """Verifica productos con stock bajo"""
        low_stock_products = Product.query.filter(
            Product.stock <= self.low_stock_threshold
        ).all()
        
        return {
            'low_stock_count': len(low_stock_products),
            'products': [p.to_dict() for p in low_stock_products]
        }
    
    async def find_similar_products(self, query: str) -> Dict[str, Any]:
        """Encuentra productos similares usando RAG"""
        similar_products = self.embedding_service.find_similar_products(query)
        return {
            'query': query,
            'similar_products': similar_products
        }
    
    async def generate_product_embeddings(self) -> Dict[str, Any]:
        """Genera embeddings para todos los productos"""
        products = Product.query.all()
        product_dicts = [p.to_dict() for p in products]
        embeddings = self.embedding_service.batch_generate_embeddings(product_dicts)
        
        # TODO: Guardar embeddings en la base de datos vectorial
        return {
            'processed_count': len(embeddings),
            'status': 'completed'
        } 