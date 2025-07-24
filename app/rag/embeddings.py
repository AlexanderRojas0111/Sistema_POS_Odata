from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import numpy as np
from app.vector_store.models import ProductEmbedding, DocumentEmbedding
from app.vector_store.config import get_vector_db

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
    def generate_embedding(self, text: str) -> List[float]:
        """Genera un embedding para un texto dado"""
        embedding = self.model.encode(text)
        return embedding.tolist()
    
    def generate_product_embedding(self, product: Dict[str, Any]) -> ProductEmbedding:
        """Genera un embedding para un producto"""
        text = f"{product['name']} {product.get('description', '')}"
        embedding = self.generate_embedding(text)
        
        return ProductEmbedding(
            product_id=product['id'],
            embedding=embedding
        )
    
    def find_similar_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Encuentra productos similares basados en una consulta"""
        query_embedding = self.generate_embedding(query)
        
        db = next(get_vector_db())
        # Usar la función de similitud coseno de pgvector
        similar_products = db.query(ProductEmbedding)\
            .order_by(ProductEmbedding.embedding.cosine_distance(query_embedding))\
            .limit(limit)\
            .all()
            
        return [p.product.to_dict() for p in similar_products]
    
    def batch_generate_embeddings(self, products: List[Dict[str, Any]]) -> List[ProductEmbedding]:
        """Genera embeddings para una lista de productos"""
        return [self.generate_product_embedding(p) for p in products] 