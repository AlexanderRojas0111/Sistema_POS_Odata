from typing import List, Optional
import numpy as np
from sqlalchemy.orm import Session
from sentence_transformers import SentenceTransformer
from app.models.product import Product, ProductEmbedding
from app.core.database import db_session

class SemanticSearchService:
    """Servicio para búsqueda semántica"""
    
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Genera un embedding para un texto
        
        Args:
            text: Texto a procesar
            
        Returns:
            Vector de embedding
        """
        return self.model.encode(text)
    
    def cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """
        Calcula la similitud coseno entre dos vectores
        
        Args:
            a: Primer vector
            b: Segundo vector
            
        Returns:
            Similitud coseno (entre -1 y 1)
        """
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    
    def search_products(self,
                       session: Session,
                       query: str,
                       limit: int = 10) -> List[Product]:
        """
        Realiza una búsqueda semántica de productos
        
        Args:
            session: Sesión de base de datos
            query: Consulta de búsqueda
            limit: Límite de resultados
            
        Returns:
            Lista de productos ordenados por relevancia
        """
        # Generar embedding para la consulta
        query_embedding = self.generate_embedding(query)
        
        # Obtener todos los productos con sus embeddings
        products_with_embeddings = session.query(Product)\
            .join(ProductEmbedding)\
            .all()
        
        # Calcular similitudes
        results = []
        for product in products_with_embeddings:
            # Usar el primer embedding del producto (podríamos mejorar esto)
            product_embedding = np.array(product.embeddings[0].embedding)
            similarity = self.cosine_similarity(query_embedding, product_embedding)
            results.append((product, similarity))
        
        # Ordenar por similitud y retornar los top N
        results.sort(key=lambda x: x[1], reverse=True)
        return [product for product, _ in results[:limit]]
    
    def hybrid_search(self,
                     session: Session,
                     query: str,
                     category: Optional[str] = None,
                     min_price: Optional[float] = None,
                     max_price: Optional[float] = None,
                     limit: int = 10) -> List[Product]:
        """
        Realiza una búsqueda híbrida combinando semántica y filtros tradicionales
        
        Args:
            session: Sesión de base de datos
            query: Consulta de búsqueda
            category: Filtro por categoría
            min_price: Precio mínimo
            max_price: Precio máximo
            limit: Límite de resultados
            
        Returns:
            Lista de productos ordenados por relevancia
        """
        # Primero aplicar filtros tradicionales
        products_query = session.query(Product)
        
        if category:
            products_query = products_query.filter(Product.category == category)
        if min_price is not None:
            products_query = products_query.filter(Product.price >= min_price)
        if max_price is not None:
            products_query = products_query.filter(Product.price <= max_price)
        
        # Obtener productos filtrados con sus embeddings
        products_with_embeddings = products_query.join(ProductEmbedding).all()
        
        # Aplicar búsqueda semántica sobre los resultados filtrados
        query_embedding = self.generate_embedding(query)
        results = []
        
        for product in products_with_embeddings:
            product_embedding = np.array(product.embeddings[0].embedding)
            similarity = self.cosine_similarity(query_embedding, product_embedding)
            results.append((product, similarity))
        
        # Ordenar por similitud y retornar los top N
        results.sort(key=lambda x: x[1], reverse=True)
        return [product for product, _ in results[:limit]] 