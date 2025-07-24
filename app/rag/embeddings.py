from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import numpy as np
from app.models import ProductEmbedding, DocumentEmbedding, Product
from app.database import db

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
        
        # Convertir el embedding de consulta a un array de NumPy
        query_vector = np.array(query_embedding)
        
        # Obtener todos los productos con sus embeddings
        products_with_embeddings = db.session.query(Product, ProductEmbedding)\
            .join(ProductEmbedding)\
            .all()
        
        # Calcular similitud coseno manualmente
        similarities = []
        for product, embedding in products_with_embeddings:
            product_vector = np.array(embedding.embedding)
            similarity = np.dot(query_vector, product_vector) / (
                np.linalg.norm(query_vector) * np.linalg.norm(product_vector)
            )
            similarities.append((similarity, product))
        
        # Ordenar por similitud y tomar los top N
        similarities.sort(reverse=True, key=lambda x: x[0])
        top_products = similarities[:limit]
        
        return [product.to_dict() for _, product in top_products]
    
    def batch_generate_embeddings(self, products: List[Dict[str, Any]]) -> List[ProductEmbedding]:
        """Genera embeddings para una lista de productos"""
        return [self.generate_product_embedding(p) for p in products] 