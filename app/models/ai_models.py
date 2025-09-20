"""
Modelos de IA - Sistema POS O'Data v2.0
=======================================
Modelos de datos para funcionalidades de inteligencia artificial.
"""

from app import db
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Index
from sqlalchemy.dialects.postgresql import ARRAY
from datetime import datetime
import json

class ProductEmbedding(db.Model):
    """Modelo para almacenar embeddings de productos"""
    __tablename__ = 'product_embeddings'
    
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, nullable=False, index=True)
    embedding_type = Column(String(50), nullable=False)  # 'tfidf', 'sentence_transformer', etc.
    embedding_vector = Column(JSON, nullable=False)  # Vector como JSON
    vector_dimension = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índices para optimización
    __table_args__ = (
        Index('idx_product_embedding_type', 'product_id', 'embedding_type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'product_id': self.product_id,
            'embedding_type': self.embedding_type,
            'vector_dimension': self.vector_dimension,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class DocumentEmbedding(db.Model):
    """Modelo para almacenar embeddings de documentos"""
    __tablename__ = 'document_embeddings'
    
    id = Column(Integer, primary_key=True)
    document_id = Column(String(100), nullable=False, index=True)
    document_type = Column(String(50), nullable=False)  # 'product_description', 'search_query', etc.
    content = Column(Text, nullable=False)
    embedding_vector = Column(JSON, nullable=False)
    vector_dimension = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Índices para optimización
    __table_args__ = (
        Index('idx_document_embedding_type', 'document_id', 'document_type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'document_id': self.document_id,
            'document_type': self.document_type,
            'content': self.content,
            'vector_dimension': self.vector_dimension,
            'created_at': self.created_at.isoformat()
        }

class AISearchLog(db.Model):
    """Modelo para registrar búsquedas de IA"""
    __tablename__ = 'ai_search_logs'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=True, index=True)
    search_query = Column(Text, nullable=False)
    search_type = Column(String(50), nullable=False)  # 'semantic', 'recommendation', 'suggestion'
    results_count = Column(Integer, default=0)
    response_time_ms = Column(Float, nullable=False)
    search_metadata = Column(JSON, nullable=True)  # Metadatos adicionales
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Índices para optimización
    __table_args__ = (
        Index('idx_ai_search_user', 'user_id', 'created_at'),
        Index('idx_ai_search_type', 'search_type', 'created_at'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'search_query': self.search_query,
            'search_type': self.search_type,
            'results_count': self.results_count,
            'response_time_ms': self.response_time_ms,
            'search_metadata': self.search_metadata,
            'created_at': self.created_at.isoformat()
        }

class AIRecommendation(db.Model):
    """Modelo para almacenar recomendaciones generadas por IA"""
    __tablename__ = 'ai_recommendations'
    
    id = Column(Integer, primary_key=True)
    source_product_id = Column(Integer, nullable=False, index=True)
    recommended_product_id = Column(Integer, nullable=False, index=True)
    similarity_score = Column(Float, nullable=False)
    recommendation_type = Column(String(50), nullable=False)  # 'content_based', 'collaborative', 'hybrid'
    recommendation_reason = Column(Text, nullable=True)
    is_active = Column(db.Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índices para optimización
    __table_args__ = (
        Index('idx_ai_recommendation_source', 'source_product_id', 'is_active'),
        Index('idx_ai_recommendation_score', 'similarity_score', 'is_active'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'source_product_id': self.source_product_id,
            'recommended_product_id': self.recommended_product_id,
            'similarity_score': self.similarity_score,
            'recommendation_type': self.recommendation_type,
            'recommendation_reason': self.recommendation_reason,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class AIVocabulary(db.Model):
    """Modelo para almacenar vocabulario de IA"""
    __tablename__ = 'ai_vocabulary'
    
    id = Column(Integer, primary_key=True)
    term = Column(String(200), nullable=False, unique=True, index=True)
    term_frequency = Column(Integer, default=1)
    document_frequency = Column(Integer, default=1)
    tfidf_score = Column(Float, default=0.0)
    term_type = Column(String(50), nullable=False)  # 'word', 'bigram', 'trigram'
    language = Column(String(10), default='es')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índices para optimización
    __table_args__ = (
        Index('idx_ai_vocabulary_term', 'term', 'language'),
        Index('idx_ai_vocabulary_tfidf', 'tfidf_score', 'term_type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'term': self.term,
            'term_frequency': self.term_frequency,
            'document_frequency': self.document_frequency,
            'tfidf_score': self.tfidf_score,
            'term_type': self.term_type,
            'language': self.language,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class AIModelStatus(db.Model):
    """Modelo para rastrear el estado de los modelos de IA"""
    __tablename__ = 'ai_model_status'
    
    id = Column(Integer, primary_key=True)
    model_name = Column(String(100), nullable=False, unique=True)
    model_version = Column(String(50), nullable=False)
    model_type = Column(String(50), nullable=False)  # 'tfidf', 'cosine_similarity', 'sentence_transformer', etc.
    is_trained = Column(db.Boolean, default=False)
    training_data_count = Column(Integer, default=0)
    last_trained_at = Column(DateTime, nullable=True)
    model_metadata = Column(JSON, nullable=True)
    performance_metrics = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'model_name': self.model_name,
            'model_version': self.model_version,
            'model_type': self.model_type,
            'is_trained': self.is_trained,
            'training_data_count': self.training_data_count,
            'last_trained_at': self.last_trained_at.isoformat() if self.last_trained_at else None,
            'model_metadata': self.model_metadata,
            'performance_metrics': self.performance_metrics,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
