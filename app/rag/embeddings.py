"""
Servicio de embeddings para funcionalidades de IA
Proporciona búsqueda semántica y recomendaciones inteligentes usando scikit-learn
"""

from typing import List, Dict, Any, Optional, Tuple
import json
import logging
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from app.core.database import db
from app.models.product import Product, ProductEmbedding

logger = logging.getLogger(__name__)

class EmbeddingService:
    """Servicio para generar y consultar embeddings de productos usando scikit-learn"""

    def __init__(self):
        # Configurar TF-IDF Vectorizer
        self.vectorizer = TfidfVectorizer(
            max_features=1000,  # Máximo 1000 características
            stop_words=None,    # Usaremos nuestras propias stop words
            lowercase=True,
            ngram_range=(1, 2), # Unigrams y bigrams
            min_df=1,          # Mínima frecuencia de documento
            max_df=0.95        # Máxima frecuencia de documento (95%)
        )
        
        # Reducción de dimensionalidad opcional
        self.svd = TruncatedSVD(n_components=100, random_state=42)
        
        # Palabras vacías en español
        self.stop_words = {
            'de', 'la', 'el', 'y', 'con', 'en', 'a', 'para', 'por', 'un', 'una', 'del', 'al', 'que', 
            'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'son', 'como', 'mas', 'pero', 'sus', 
            'ya', 'o', 'este', 'si', 'porque', 'esta', 'entre', 'cuando', 'muy', 'sin', 'sobre', 
            'tambien', 'me', 'hasta', 'hay', 'donde', 'quien', 'desde', 'todo', 'nos', 'durante', 
            'todos', 'uno', 'les', 'ni', 'contra', 'otros', 'ese', 'eso', 'ante', 'ellos', 'e', 
            'esto', 'mi', 'antes', 'algunos', 'unos', 'yo', 'otro', 'otras', 'otra', 'tanto', 
            'esa', 'estos', 'mucho', 'quienes', 'nada', 'muchos', 'cual', 'poco', 'ella', 'estar', 
            'estas', 'algunas', 'algo', 'nosotros', 'tu', 'ti', 'tus', 'ellas', 'nosotras'
        }
        
        # Matrices y datos cacheados
        self.tfidf_matrix = None
        self.product_ids = []
        self.products_data = []
        self.is_fitted = False
        self.total_documents = 0
        
        # No inicializar automáticamente - se hará cuando sea necesario
        # self._initialize_embeddings()

    def _prepare_text(self, text: str) -> str:
        """Prepara el texto para procesamiento: limpia y tokeniza"""
        if not text:
            return ""
        
        # Convertir a minúsculas
        text = text.lower()
        
        # Remover caracteres especiales, mantener solo letras, números y espacios
        text = re.sub(r'[^a-záéíóúüñ0-9\s]', ' ', text)
        
        # Remover espacios múltiples
        text = re.sub(r'\s+', ' ', text)
        
        # Filtrar palabras vacías
        words = text.split()
        filtered_words = [word for word in words if word not in self.stop_words and len(word) > 2]
        
        return ' '.join(filtered_words)

    def _initialize_embeddings(self):
        """Inicializa los embeddings con todos los productos existentes"""
        try:
            products = Product.query.all()
            
            if not products:
                logger.warning("No hay productos en la base de datos para inicializar embeddings")
                return
            
            # Preparar textos de productos
            texts = []
            self.product_ids = []
            self.products_data = []
            
            for product in products:
                text = f"{product.name} {product.description} {product.category}"
                prepared_text = self._prepare_text(text)
                
                texts.append(prepared_text)
                self.product_ids.append(product.id)
                self.products_data.append({
                    'id': product.id,
                    'name': product.name,
                    'description': product.description,
                    'category': product.category,
                    'price': product.price,
                    'stock': product.stock
                })
            
            # Entrenar el vectorizador TF-IDF
            self.tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # Aplicar reducción de dimensionalidad si hay suficientes productos y características
            if len(products) > 10 and self.tfidf_matrix.shape[1] > 100:
                self.tfidf_matrix = self.svd.fit_transform(self.tfidf_matrix)
            
            self.is_fitted = True
            
            logger.info(f"Embeddings inicializados para {len(products)} productos. "
                       f"Dimensiones de la matriz: {self.tfidf_matrix.shape}")
            
        except Exception as e:
            logger.error(f"Error inicializando embeddings: {e}")
            self.is_fitted = False

    def generate_product_embedding(self, product: Product) -> Dict[str, Any]:
        """Genera embedding para un producto específico"""
        try:
            if not self.is_fitted:
                logger.warning("El vectorizador no está entrenado. Inicializando...")
                self._initialize_embeddings()
                
            if not self.is_fitted:
                return {}
            
            # Preparar texto del producto
            text = f"{product.name} {product.description} {product.category}"
            prepared_text = self._prepare_text(text)
            
            # Generar vector TF-IDF
            tfidf_vector = self.vectorizer.transform([prepared_text])
            
            # Aplicar reducción de dimensionalidad si está disponible y fue entrenada
            if hasattr(self.svd, 'components_') and self.tfidf_matrix.shape[1] <= 100:
                tfidf_vector = self.svd.transform(tfidf_vector)
            
            # Convertir a array numpy para facilitar el manejo
            vector_array = tfidf_vector.toarray()[0]
            
            embedding_data = {
                'product_id': product.id,
                'vector': vector_array.tolist(),
                'vector_shape': vector_array.shape,
                'magnitude': float(np.linalg.norm(vector_array))
            }
            
            return embedding_data
            
        except Exception as e:
            logger.error(f"Error generando embedding para producto {product.id}: {e}")
            return {}

    def find_similar_products(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Encuentra productos similares basado en una consulta de texto"""
        try:
            if not self.is_fitted:
                logger.warning("El vectorizador no está entrenado. Inicializando...")
                self._initialize_embeddings()
                
            if not self.is_fitted:
                return []
            
            # Preparar consulta
            prepared_query = self._prepare_text(query)
            
            if not prepared_query.strip():
                return []
            
            # Generar vector TF-IDF para la consulta
            query_vector = self.vectorizer.transform([prepared_query])
            
            # Aplicar reducción de dimensionalidad si está disponible y fue entrenada
            if hasattr(self.svd, 'components_') and self.tfidf_matrix.shape[1] <= 100:
                query_vector = self.svd.transform(query_vector)
            
            # Calcular similitudes coseno
            similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]
            
            # Obtener índices ordenados por similitud
            similar_indices = np.argsort(similarities)[::-1]
            
            # Filtrar por umbral mínimo de similitud
            min_similarity = 0.1
            results = []
            
            for idx in similar_indices[:limit * 2]:  # Obtener más para filtrar
                similarity_score = similarities[idx]
                
                if similarity_score < min_similarity:
                    continue
                
                if len(results) >= limit:
                    break
                
                product_data = self.products_data[idx].copy()
                product_data['similarity_score'] = float(similarity_score)
                
                # Encontrar términos coincidentes
                product_text = f"{product_data['name']} {product_data['description']} {product_data['category']}"
                product_words = set(self._prepare_text(product_text).split())
                query_words = set(prepared_query.split())
                matching_terms = list(product_words & query_words)
                product_data['matching_terms'] = matching_terms
                
                results.append(product_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error buscando productos similares: {e}")
            return []

    def generate_recommendations(self, product_id: int, limit: int = 3) -> List[Dict[str, Any]]:
        """Genera recomendaciones basadas en un producto específico"""
        try:
            if not self.is_fitted:
                self._initialize_embeddings()
                
            if not self.is_fitted:
                return []
            
            # Encontrar el índice del producto
            try:
                product_idx = self.product_ids.index(product_id)
            except ValueError:
                logger.warning(f"Producto {product_id} no encontrado en embeddings")
                return []
            
            # Obtener el vector del producto
            product_vector = self.tfidf_matrix[product_idx:product_idx+1]
            
            # Calcular similitudes con todos los productos
            similarities = cosine_similarity(product_vector, self.tfidf_matrix)[0]
            
            # Obtener índices ordenados por similitud (excluyendo el producto original)
            similar_indices = np.argsort(similarities)[::-1]
            
            recommendations = []
            for idx in similar_indices:
                if idx == product_idx:  # Saltar el producto original
                    continue
                
                similarity_score = similarities[idx]
                
                if similarity_score < 0.1:  # Umbral mínimo
                    continue
                
                if len(recommendations) >= limit:
                    break
                
                product_data = self.products_data[idx].copy()
                product_data['similarity_score'] = float(similarity_score)
                product_data['recommendation_reason'] = self._get_recommendation_reason(
                    self.products_data[product_idx], product_data
                )
                
                recommendations.append(product_data)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generando recomendaciones para producto {product_id}: {e}")
            return []

    def _get_recommendation_reason(self, base_product: Dict, recommended_product: Dict) -> str:
        """Genera una razón para la recomendación"""
        reasons = []
        
        # Misma categoría
        if base_product['category'] == recommended_product['category']:
            reasons.append(f"misma categoría ({base_product['category']})")
        
        # Rango de precio similar
        price_diff = abs(base_product['price'] - recommended_product['price'])
        if price_diff <= base_product['price'] * 0.3:  # Diferencia menor al 30%
            reasons.append("precio similar")
        
        # Términos comunes en el nombre
        base_words = set(base_product['name'].lower().split())
        rec_words = set(recommended_product['name'].lower().split())
        common_words = base_words & rec_words
        if common_words:
            reasons.append(f"ingredientes similares ({', '.join(common_words)})")
        
        if not reasons:
            return "características similares"
        
        return ", ".join(reasons)

    def update_embeddings_for_all_products(self) -> Dict[str, Any]:
        """Actualiza los embeddings para todos los productos"""
        try:
            logger.info("Actualizando embeddings para todos los productos...")
            
            # Reinicializar embeddings
            self._initialize_embeddings()
            
            if self.is_fitted:
                return {
                    'success': True,
                    'updated_products': len(self.product_ids),
                    'matrix_shape': list(self.tfidf_matrix.shape),
                    'vocabulary_size': len(self.vectorizer.vocabulary_) if hasattr(self.vectorizer, 'vocabulary_') else 0
                }
            else:
                return {'success': False, 'error': 'No se pudieron inicializar los embeddings'}
            
        except Exception as e:
            logger.error(f"Error actualizando embeddings: {e}")
            return {'success': False, 'error': str(e)}

    def get_search_suggestions(self, partial_query: str, limit: int = 5) -> List[str]:
        """Genera sugerencias de búsqueda basadas en una consulta parcial"""
        try:
            if not self.is_fitted or not hasattr(self.vectorizer, 'vocabulary_'):
                return []
            
            if not partial_query or len(partial_query) < 2:
                return []
            
            partial_query = partial_query.lower()
            
            # Buscar en el vocabulario del vectorizador
            vocabulary = self.vectorizer.vocabulary_
            matching_terms = [
                term for term in vocabulary.keys() 
                if term.startswith(partial_query) and len(term) > 2
            ]
            
            # Ordenar por frecuencia (términos con índices más bajos son más frecuentes)
            matching_terms.sort(key=lambda x: vocabulary[x])
            
            return matching_terms[:limit]
            
        except Exception as e:
            logger.error(f"Error generando sugerencias: {e}")
            return []

    def get_embedding_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas del sistema de embeddings"""
        try:
            stats = {
                'is_fitted': self.is_fitted,
                'total_products': len(self.product_ids),
                'vocabulary_size': len(self.vectorizer.vocabulary_) if hasattr(self.vectorizer, 'vocabulary_') else 0,
                'matrix_shape': list(self.tfidf_matrix.shape) if self.tfidf_matrix is not None else None,
                'svd_components': self.svd.n_components if hasattr(self.svd, 'components_') else None
            }
            
            if hasattr(self.vectorizer, 'vocabulary_'):
                # Top términos más frecuentes
                vocab_items = list(self.vectorizer.vocabulary_.items())
                vocab_items.sort(key=lambda x: x[1])  # Ordenar por índice (frecuencia)
                stats['top_terms'] = [term for term, idx in vocab_items[:10]]
            
            return stats
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {'error': str(e)}

    def search_by_category(self, category: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Busca productos por categoría específica"""
        try:
            results = []
            for product_data in self.products_data:
                if product_data['category'].lower() == category.lower():
                    results.append(product_data.copy())
                    if len(results) >= limit:
                        break
            
            return results
            
        except Exception as e:
            logger.error(f"Error buscando por categoría {category}: {e}")
            return []