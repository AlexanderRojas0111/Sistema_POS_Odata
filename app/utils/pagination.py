#!/usr/bin/env python3
"""
Sistema de Paginación - O'Data v2.0.0
======================================

Sistema para:
- Paginación de resultados
- Ordenamiento
- Filtros
- Optimización de queries

Autor: Sistema POS Odata
Versión: 2.0.0
"""

from typing import Dict, List, Any, Optional, Tuple
from flask import request, jsonify
from sqlalchemy import desc, asc
from sqlalchemy.orm import Query
import math

class PaginationHelper:
    """Helper para paginación y ordenamiento"""
    
    def __init__(self, 
                 default_page: int = 1,
                 default_per_page: int = 20,
                 max_per_page: int = 100):
        self.default_page = default_page
        self.default_per_page = default_per_page
        self.max_per_page = max_per_page
    
    def get_pagination_params(self) -> Tuple[int, int, int]:
        """Obtener parámetros de paginación desde request"""
        try:
            page = max(1, int(request.args.get('page', self.default_page)))
        except (ValueError, TypeError):
            page = self.default_page
        
        try:
            per_page = min(
                self.max_per_page,
                max(1, int(request.args.get('per_page', self.default_per_page)))
            )
        except (ValueError, TypeError):
            per_page = self.default_per_page
        
        offset = (page - 1) * per_page
        
        return page, per_page, offset
    
    def get_sorting_params(self, allowed_fields: List[str], default_field: str = 'id') -> Tuple[str, str]:
        """Obtener parámetros de ordenamiento"""
        sort_by = request.args.get('sort_by', default_field)
        if sort_by not in allowed_fields:
            sort_by = default_field
        
        sort_order = request.args.get('sort_order', 'asc').lower()
        if sort_order not in ['asc', 'desc']:
            sort_order = 'asc'
        
        return sort_by, sort_order
    
    def apply_sorting(self, query: Query, sort_by: str, sort_order: str) -> Query:
        """Aplicar ordenamiento a la query"""
        if hasattr(query.model, sort_by):
            sort_column = getattr(query.model, sort_by)
            if sort_order == 'desc':
                return query.order_by(desc(sort_column))
            else:
                return query.order_by(asc(sort_column))
        return query
    
    def paginate_query(self, query: Query, page: int, per_page: int) -> Tuple[List, int, Dict]:
        """Paginación de query SQLAlchemy"""
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        
        pagination_info = self._create_pagination_info(page, per_page, total)
        
        return items, total, pagination_info
    
    def _create_pagination_info(self, page: int, per_page: int, total: int) -> Dict[str, Any]:
        """Crear información de paginación"""
        total_pages = math.ceil(total / per_page) if total > 0 else 0
        
        return {
            'page': page,
            'per_page': per_page,
            'total': total,
            'total_pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_page': page - 1 if page > 1 else None,
            'next_page': page + 1 if page < total_pages else None,
            'pages': self._get_page_range(page, total_pages),
            'showing': {
                'from': (page - 1) * per_page + 1 if total > 0 else 0,
                'to': min(page * per_page, total)
            }
        }
    
    def _get_page_range(self, current_page: int, total_pages: int, max_pages: int = 5) -> List[int]:
        """Obtener rango de páginas para mostrar"""
        if total_pages <= max_pages:
            return list(range(1, total_pages + 1))
        
        start = max(1, current_page - max_pages // 2)
        end = min(total_pages, start + max_pages - 1)
        
        if end - start + 1 < max_pages:
            start = max(1, end - max_pages + 1)
        
        return list(range(start, end + 1))

class FilterHelper:
    """Helper para filtros de búsqueda"""
    
    def __init__(self, allowed_filters: Dict[str, str]):
        """
        allowed_filters: Dict con nombre del filtro y tipo de operación
        Ejemplo: {'name': 'like', 'price': 'range', 'category': 'exact'}
        """
        self.allowed_filters = allowed_filters
    
    def get_filters(self) -> Dict[str, Any]:
        """Obtener filtros desde request"""
        filters = {}
        
        for filter_name, filter_type in self.allowed_filters.items():
            filter_value = request.args.get(filter_name)
            if filter_value is not None and filter_value != '':
                filters[filter_name] = {
                    'value': filter_value,
                    'type': filter_type
                }
        
        return filters
    
    def apply_filters(self, query: Query, filters: Dict[str, Any]) -> Query:
        """Aplicar filtros a la query"""
        for filter_name, filter_info in filters.items():
            if filter_name in self.allowed_filters:
                query = self._apply_single_filter(query, filter_name, filter_info)
        
        return query
    
    def _apply_single_filter(self, query: Query, filter_name: str, filter_info: Dict[str, Any]) -> Query:
        """Aplicar un filtro individual"""
        filter_type = filter_info['type']
        filter_value = filter_info['value']
        
        if not hasattr(query.model, filter_name):
            return query
        
        column = getattr(query.model, filter_name)
        
        if filter_type == 'exact':
            query = query.filter(column == filter_value)
        elif filter_type == 'like':
            query = query.filter(column.ilike(f'%{filter_value}%'))
        elif filter_type == 'startswith':
            query = query.filter(column.ilike(f'{filter_value}%'))
        elif filter_type == 'endswith':
            query = query.filter(column.ilike(f'%{filter_value}'))
        elif filter_type == 'range':
            # Para rangos como "min-max" o ">min" o "<max"
            if '-' in str(filter_value):
                min_val, max_val = filter_value.split('-', 1)
                if min_val and max_val:
                    query = query.filter(column >= min_val, column <= max_val)
                elif min_val:
                    query = query.filter(column >= min_val)
                elif max_val:
                    query = query.filter(column <= max_val)
            elif str(filter_value).startswith('>'):
                val = filter_value[1:]
                query = query.filter(column > val)
            elif str(filter_value).startswith('<'):
                val = filter_value[1:]
                query = query.filter(column < val)
            elif str(filter_value).startswith('>='):
                val = filter_value[2:]
                query = query.filter(column >= val)
            elif str(filter_value).startswith('<='):
                val = filter_value[2:]
                query = query.filter(column <= val)
        elif filter_type == 'in':
            # Para valores separados por comas
            values = [v.strip() for v in str(filter_value).split(',')]
            query = query.filter(column.in_(values))
        elif filter_type == 'boolean':
            # Para valores booleanos
            bool_value = str(filter_value).lower() in ['true', '1', 'yes', 'on']
            query = query.filter(column == bool_value)
        
        return query

class SearchHelper:
    """Helper para búsqueda de texto"""
    
    def __init__(self, searchable_fields: List[str]):
        self.searchable_fields = searchable_fields
    
    def get_search_query(self) -> Optional[str]:
        """Obtener query de búsqueda"""
        return request.args.get('q', '').strip()
    
    def apply_search(self, query: Query, search_query: str) -> Query:
        """Aplicar búsqueda de texto a la query"""
        if not search_query or not self.searchable_fields:
            return query
        
        from sqlalchemy import or_
        
        search_conditions = []
        for field_name in self.searchable_fields:
            if hasattr(query.model, field_name):
                field = getattr(query.model, field_name)
                search_conditions.append(field.ilike(f'%{search_query}%'))
        
        if search_conditions:
            query = query.filter(or_(*search_conditions))
        
        return query

def create_paginated_response(items: List, pagination_info: Dict, 
                            serializer_func=None, **extra_data) -> Dict[str, Any]:
    """Crear respuesta paginada estandarizada"""
    response = {
        'success': True,
        'data': items,
        'pagination': pagination_info,
        'meta': {
            'total_items': pagination_info['total'],
            'current_page': pagination_info['page'],
            'items_per_page': pagination_info['per_page'],
            'total_pages': pagination_info['total_pages']
        }
    }
    
    # Serializar items si se proporciona función
    if serializer_func and callable(serializer_func):
        response['data'] = [serializer_func(item) for item in items]
    
    # Agregar datos extra
    response.update(extra_data)
    
    return response

def create_error_response(message: str, status_code: int = 400, **extra_data) -> Tuple[Dict[str, Any], int]:
    """Crear respuesta de error estandarizada"""
    response = {
        'success': False,
        'error': message,
        'status_code': status_code
    }
    response.update(extra_data)
    
    return response, status_code

# Instancias globales con configuración por defecto
pagination_helper = PaginationHelper()
filter_helper = FilterHelper({})
search_helper = SearchHelper([])

def setup_pagination(default_page: int = 1, default_per_page: int = 20, max_per_page: int = 100):
    """Configurar paginación global"""
    global pagination_helper
    pagination_helper = PaginationHelper(default_page, default_per_page, max_per_page)

def setup_filters(allowed_filters: Dict[str, str]):
    """Configurar filtros globales"""
    global filter_helper
    filter_helper = FilterHelper(allowed_filters)

def setup_search(searchable_fields: List[str]):
    """Configurar búsqueda global"""
    global search_helper
    search_helper = SearchHelper(searchable_fields)
