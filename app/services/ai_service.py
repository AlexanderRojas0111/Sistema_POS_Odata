"""
Servicio de IA - Sistema POS O'Data v2.0
========================================
Servicio principal para funcionalidades de inteligencia artificial.
"""

import numpy as np
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer

from app import db
from app.models.ai_models import (
    ProductEmbedding, DocumentEmbedding, AISearchLog, 
    AIRecommendation, AIVocabulary, AIModelStatus
)
from app.models.product import Product

logger = logging.getLogger(__name__)

class AIService:
    """Servicio principal de IA para el sistema POS"""
    
    def __init__(self):
        self.tfidf_vectorizer = None
        self.tfidf_matrix = None
        self.svd_transformer = None
        self.vocabulary = {}
        self.stop_words_es = set()
        self.stemmer = None
        self._initialize_nltk()
    
    def _initialize_nltk(self):
        """Inicializar recursos de NLTK"""
        try:
            # Descargar recursos necesarios
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            
            # Configurar stop words en español
            self.stop_words_es = set(stopwords.words('spanish'))
            
            # Configurar stemmer
            self.stemmer = SnowballStemmer('spanish')
            
            logger.info("NLTK resources initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing NLTK: {e}")
            self.stop_words_es = set()
            self.stemmer = None
    
    def preprocess_text(self, text: str) -> str:
        """Preprocesar texto para análisis de IA"""
        if not text:
            return ""
        
        # Convertir a minúsculas
        text = text.lower()
        
        # Limpiar caracteres especiales
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Tokenizar
        tokens = word_tokenize(text, language='spanish')
        
        # Filtrar stop words y palabras muy cortas
        tokens = [token for token in tokens 
                 if token not in self.stop_words_es and len(token) > 2]
        
        # Aplicar stemming
        if self.stemmer:
            tokens = [self.stemmer.stem(token) for token in tokens]
        
        return ' '.join(tokens)
    
    def train_tfidf_model(self, products: List[Product]) -> bool:
        """Entrenar modelo TF-IDF con productos"""
        try:
            # Preparar textos de productos
            product_texts = []
            for product in products:
                # Combinar nombre, descripción y categoría
                text_parts = []
                if product.name:
                    text_parts.append(product.name)
                if hasattr(product, 'description') and product.description:
                    text_parts.append(product.description)
                if hasattr(product, 'category') and product.category:
                    text_parts.append(product.category)
                
                combined_text = ' '.join(text_parts)
                processed_text = self.preprocess_text(combined_text)
                product_texts.append(processed_text)
            
            # Configurar TF-IDF
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),
                stop_words=list(self.stop_words_es),
                min_df=1,
                max_df=0.95
            )
            
            # Entrenar modelo
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(product_texts)
            
            # Guardar vocabulario en base de datos
            self._save_vocabulary()
            
            # Actualizar estado del modelo
            self._update_model_status('tfidf', '1.0.0', True, len(products))
            
            logger.info(f"TF-IDF model trained with {len(products)} products")
            return True
            
        except Exception as e:
            logger.error(f"Error training TF-IDF model: {e}")
            return False
    
    def _save_vocabulary(self):
        """Guardar vocabulario en base de datos"""
        try:
            if not self.tfidf_vectorizer:
                return
            
            vocabulary = self.tfidf_vectorizer.vocabulary_
            idf_scores = self.tfidf_vectorizer.idf_
            
            for term, term_id in vocabulary.items():
                # Verificar si el término ya existe
                existing = AIVocabulary.query.filter_by(term=term).first()
                
                if existing:
                    existing.term_frequency += 1
                    existing.tfidf_score = float(idf_scores[term_id])
                    existing.updated_at = datetime.utcnow()
                else:
                    new_term = AIVocabulary(
                        term=term,
                        term_frequency=1,
                        document_frequency=1,
                        tfidf_score=float(idf_scores[term_id]),
                        term_type='word' if ' ' not in term else 'bigram',
                        language='es'
                    )
                    db.session.add(new_term)
            
            db.session.commit()
            logger.info("Vocabulary saved to database")
            
        except Exception as e:
            logger.error(f"Error saving vocabulary: {e}")
            db.session.rollback()
    
    def _update_model_status(self, model_name: str, version: str, is_trained: bool, data_count: int):
        """Actualizar estado del modelo en base de datos"""
        try:
            model_status = AIModelStatus.query.filter_by(model_name=model_name).first()
            
            if model_status:
                model_status.model_version = version
                model_status.is_trained = is_trained
                model_status.training_data_count = data_count
                model_status.last_trained_at = datetime.utcnow() if is_trained else None
                model_status.updated_at = datetime.utcnow()
            else:
                model_status = AIModelStatus(
                    model_name=model_name,
                    model_version=version,
                    model_type=model_name,
                    is_trained=is_trained,
                    training_data_count=data_count,
                    last_trained_at=datetime.utcnow() if is_trained else None
                )
                db.session.add(model_status)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error updating model status: {e}")
            db.session.rollback()
    
    def semantic_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Realizar búsqueda semántica de productos"""
        start_time = datetime.utcnow()
        
        try:
            if not self.tfidf_vectorizer or self.tfidf_matrix is None:
                logger.warning("TF-IDF model not trained")
                return []
            
            # Preprocesar consulta
            processed_query = self.preprocess_text(query)
            
            # Transformar consulta
            query_vector = self.tfidf_vectorizer.transform([processed_query])
            
            # Calcular similitudes
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            
            # Obtener productos
            products = Product.query.filter(Product.is_active == True).all()
            
            # Crear resultados con similitudes
            results = []
            for i, product in enumerate(products):
                if i < len(similarities):
                    similarity_score = float(similarities[i])
                    if similarity_score > 0.1:  # Umbral mínimo
                        results.append({
                            'product': product.to_dict(),
                            'similarity_score': similarity_score,
                            'matched_terms': self._get_matched_terms(query, product)
                        })
            
            # Ordenar por similitud
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Limitar resultados
            results = results[:limit]
            
            # Registrar búsqueda
            response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self._log_search(query, 'semantic', len(results), response_time)
            
            return results
            
        except Exception as e:
            logger.error(f"Error in semantic search: {e}")
            return []
    
    def _get_matched_terms(self, query: str, product: Product) -> List[str]:
        """Obtener términos que coincidieron en la búsqueda"""
        try:
            query_terms = set(self.preprocess_text(query).split())
            product_text = self.preprocess_text(f"{product.name} {getattr(product, 'description', '')}")
            product_terms = set(product_text.split())
            
            return list(query_terms.intersection(product_terms))
        except:
            return []
    
    def get_recommendations(self, product_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Obtener recomendaciones para un producto"""
        try:
            if not self.tfidf_vectorizer or self.tfidf_matrix is None:
                return []
            
            # Obtener producto
            product = Product.query.get(product_id)
            if not product:
                return []
            
            # Obtener índice del producto en la matriz
            products = Product.query.filter(Product.is_active == True).all()
            product_index = None
            for i, p in enumerate(products):
                if p.id == product_id:
                    product_index = i
                    break
            
            if product_index is None:
                return []
            
            # Calcular similitudes
            product_vector = self.tfidf_matrix[product_index:product_index+1]
            similarities = cosine_similarity(product_vector, self.tfidf_matrix).flatten()
            
            # Crear recomendaciones
            recommendations = []
            for i, similarity_score in enumerate(similarities):
                if i != product_index and similarity_score > 0.1:
                    recommended_product = products[i]
                    recommendations.append({
                        'product': recommended_product.to_dict(),
                        'similarity_score': float(similarity_score),
                        'recommendation_reason': self._get_recommendation_reason(product, recommended_product, similarity_score)
                    })
            
            # Ordenar por similitud
            recommendations.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Limitar resultados
            recommendations = recommendations[:limit]
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return []
    
    def _get_recommendation_reason(self, source_product: Product, recommended_product: Product, similarity: float) -> str:
        """Generar razón para la recomendación"""
        reasons = []
        
        # Misma categoría
        if (hasattr(source_product, 'category') and hasattr(recommended_product, 'category') and 
            source_product.category == recommended_product.category):
            reasons.append("misma categoría")
        
        # Precio similar
        if (hasattr(source_product, 'price') and hasattr(recommended_product, 'price')):
            price_diff = abs(source_product.price - recommended_product.price) / source_product.price
            if price_diff < 0.3:
                reasons.append("precio similar")
        
        # Similitud alta
        if similarity > 0.5:
            reasons.append("productos muy similares")
        elif similarity > 0.3:
            reasons.append("productos relacionados")
        
        return ", ".join(reasons) if reasons else "producto relacionado"
    
    def get_search_suggestions(self, query: str, limit: int = 10) -> List[str]:
        """Obtener sugerencias de búsqueda"""
        try:
            if not query or len(query) < 2:
                return []
            
            # Buscar términos en vocabulario
            suggestions = AIVocabulary.query.filter(
                AIVocabulary.term.like(f"%{query.lower()}%")
            ).order_by(AIVocabulary.tfidf_score.desc()).limit(limit).all()
            
            return [s.term for s in suggestions]
            
        except Exception as e:
            logger.error(f"Error getting search suggestions: {e}")
            return []
    
    def _log_search(self, query: str, search_type: str, results_count: int, response_time_ms: float, user_id: int = None):
        """Registrar búsqueda en logs"""
        try:
            search_log = AISearchLog(
                user_id=user_id,
                search_query=query,
                search_type=search_type,
                results_count=results_count,
                response_time_ms=response_time_ms
            )
            db.session.add(search_log)
            db.session.commit()
        except Exception as e:
            logger.error(f"Error logging search: {e}")
            db.session.rollback()
    
    def get_ai_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas del sistema de IA"""
        try:
            stats = {
                'models': {},
                'vocabulary_size': AIVocabulary.query.count(),
                'total_searches': AISearchLog.query.count(),
                'total_recommendations': AIRecommendation.query.count()
            }
            
            # Estadísticas de modelos
            model_statuses = AIModelStatus.query.all()
            for model in model_statuses:
                stats['models'][model.model_name] = {
                    'version': model.model_version,
                    'is_trained': model.is_trained,
                    'training_data_count': model.training_data_count,
                    'last_trained': model.last_trained_at.isoformat() if model.last_trained_at else None
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting AI stats: {e}")
            return {}
    
    def initialize_ai_system(self) -> bool:
        """Inicializar sistema de IA con datos existentes"""
        try:
            # Obtener productos activos
            products = Product.query.filter(Product.is_active == True).all()
            
            if not products:
                logger.warning("No products found for AI initialization")
                return False
            
            # Entrenar modelo TF-IDF
            success = self.train_tfidf_model(products)
            
            if success:
                logger.info(f"AI system initialized with {len(products)} products")
                return True
            else:
                logger.error("Failed to initialize AI system")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing AI system: {e}")
            return False
