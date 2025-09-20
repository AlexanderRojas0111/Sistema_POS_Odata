"""
Base Repository - Sistema POS O'Data
===================================
Repository base con operaciones CRUD genéricas.
"""

from typing import TypeVar, Generic, List, Optional, Dict, Any
from sqlalchemy.orm import Query
from app import db
from app.exceptions import NotFoundError, DatabaseError

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Repository base con operaciones CRUD genéricas"""
    
    def __init__(self, model_class: type):
        self.model_class = model_class
        self.db = db
    
    def create(self, **kwargs) -> T:
        """Crear nueva entidad"""
        try:
            entity = self.model_class(**kwargs)
            db.session.add(entity)
            db.session.commit()
            return entity
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Error creating {self.model_class.__name__}: {str(e)}")
    
    def get_by_id(self, entity_id: int) -> Optional[T]:
        """Obtener entidad por ID"""
        return self.model_class.query.get(entity_id)
    
    def get_by_id_or_404(self, entity_id: int) -> T:
        """Obtener entidad por ID o lanzar 404"""
        entity = self.get_by_id(entity_id)
        if not entity:
            raise NotFoundError(self.model_class.__name__, entity_id)
        return entity
    
    def get_all(self, page: int = 1, per_page: int = 20, **filters) -> Dict[str, Any]:
        """Obtener todas las entidades con paginación"""
        query = self._apply_filters(self.model_class.query, **filters)
        
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return {
            'items': pagination.items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
    
    def update(self, entity_id: int, **kwargs) -> T:
        """Actualizar entidad"""
        try:
            entity = self.get_by_id_or_404(entity_id)
            
            for key, value in kwargs.items():
                if hasattr(entity, key):
                    setattr(entity, key, value)
            
            db.session.commit()
            return entity
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Error updating {self.model_class.__name__}: {str(e)}")
    
    def delete(self, entity_id: int) -> bool:
        """Eliminar entidad"""
        try:
            entity = self.get_by_id_or_404(entity_id)
            db.session.delete(entity)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            raise DatabaseError(f"Error deleting {self.model_class.__name__}: {str(e)}")
    
    def count(self, **filters) -> int:
        """Contar entidades con filtros"""
        query = self._apply_filters(self.model_class.query, **filters)
        return query.count()
    
    def exists(self, entity_id: int) -> bool:
        """Verificar si existe entidad"""
        return self.model_class.query.filter_by(id=entity_id).first() is not None
    
    def _apply_filters(self, query: Query, **filters) -> Query:
        """Aplicar filtros a la consulta"""
        for key, value in filters.items():
            if hasattr(self.model_class, key) and value is not None:
                if isinstance(value, str):
                    # Búsqueda parcial para strings
                    query = query.filter(getattr(self.model_class, key).contains(value))
                else:
                    # Búsqueda exacta para otros tipos
                    query = query.filter(getattr(self.model_class, key) == value)
        
        return query
    
    def search(self, search_term: str, search_fields: List[str], page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """Búsqueda en múltiples campos"""
        query = self.model_class.query
        
        # Crear condiciones de búsqueda
        search_conditions = []
        for field in search_fields:
            if hasattr(self.model_class, field):
                search_conditions.append(
                    getattr(self.model_class, field).contains(search_term)
                )
        
        if search_conditions:
            from sqlalchemy import or_
            query = query.filter(or_(*search_conditions))
        
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return {
            'items': pagination.items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
