from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.product import Product
from app.core.database import db_session

class ProductService:
    """Servicio para la gestión de productos"""
    
    def get_products(self, 
                    session: Session,
                    page: int = 1,
                    per_page: int = 10,
                    category: Optional[str] = None) -> Dict[str, Any]:
        """
        Obtiene una lista paginada de productos
        
        Args:
            session: Sesión de base de datos
            page: Número de página
            per_page: Elementos por página
            category: Filtro por categoría
            
        Returns:
            Dict con items, total, páginas y página actual
        """
        query = session.query(Product)
        
        if category:
            query = query.filter(Product.category == category)
            
        products = query.paginate(page=page, per_page=per_page)
        
        return {
            'items': [product.to_dict() for product in products.items],
            'total': products.total,
            'pages': products.pages,
            'current_page': products.page
        }
    
    def get_product_by_id(self, session: Session, product_id: int) -> Optional[Product]:
        """
        Obtiene un producto por su ID
        
        Args:
            session: Sesión de base de datos
            product_id: ID del producto
            
        Returns:
            Producto o None si no existe
        """
        return session.query(Product).get(product_id)
    
    def create_product(self, session: Session, data: Dict[str, Any]) -> Product:
        """
        Crea un nuevo producto
        
        Args:
            session: Sesión de base de datos
            data: Datos del producto
            
        Returns:
            Producto creado
        """
        product = Product(**data)
        session.add(product)
        session.commit()
        return product
    
    def update_product(self, 
                      session: Session,
                      product_id: int,
                      data: Dict[str, Any]) -> Optional[Product]:
        """
        Actualiza un producto existente
        
        Args:
            session: Sesión de base de datos
            product_id: ID del producto
            data: Datos a actualizar
            
        Returns:
            Producto actualizado o None si no existe
        """
        product = self.get_product_by_id(session, product_id)
        if product:
            for key, value in data.items():
                if hasattr(product, key):
                    setattr(product, key, value)
            session.commit()
        return product
    
    def delete_product(self, session: Session, product_id: int) -> bool:
        """
        Elimina un producto
        
        Args:
            session: Sesión de base de datos
            product_id: ID del producto
            
        Returns:
            True si se eliminó, False si no existía
        """
        product = self.get_product_by_id(session, product_id)
        if product:
            session.delete(product)
            session.commit()
            return True
        return False
    
    def get_low_stock_products(self, session: Session, threshold: int) -> List[Product]:
        """
        Obtiene productos con stock bajo
        
        Args:
            session: Sesión de base de datos
            threshold: Umbral de stock bajo
            
        Returns:
            Lista de productos con stock bajo
        """
        return session.query(Product)\
            .join(Product.inventory)\
            .filter(Product.quantity <= threshold)\
            .all()
    
    def search_products(self, 
                       session: Session,
                       query: str,
                       limit: int = 10) -> List[Product]:
        """
        Busca productos por nombre o descripción
        
        Args:
            session: Sesión de base de datos
            query: Término de búsqueda
            limit: Límite de resultados
            
        Returns:
            Lista de productos que coinciden
        """
        search = f"%{query}%"
        return session.query(Product)\
            .filter(
                (Product.name.ilike(search)) |
                (Product.description.ilike(search))
            )\
            .limit(limit)\
            .all() 