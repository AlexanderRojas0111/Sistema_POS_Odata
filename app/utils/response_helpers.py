"""
Helpers de Respuesta - Sistema POS O'Data
========================================
Utilidades para respuestas consistentes de la API
"""

from flask import jsonify
from typing import Any, Dict, Optional, Union
from datetime import datetime

def success_response(
    data: Any = None, 
    message: str = "Operación exitosa", 
    status_code: int = 200,
    meta: Optional[Dict] = None
) -> tuple:
    """
    Crear respuesta de éxito estandarizada
    
    Args:
        data: Datos de respuesta
        message: Mensaje de éxito
        status_code: Código de estado HTTP
        meta: Metadatos adicionales
    
    Returns:
        Tupla (response, status_code)
    """
    response = {
        "success": True,
        "message": message,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    if meta:
        response["meta"] = meta
    
    return jsonify(response), status_code

def error_response(
    message: str = "Error en la operación",
    status_code: int = 400,
    error_code: Optional[str] = None,
    details: Optional[Dict] = None
) -> tuple:
    """
    Crear respuesta de error estandarizada
    
    Args:
        message: Mensaje de error
        status_code: Código de estado HTTP
        error_code: Código de error específico
        details: Detalles adicionales del error
    
    Returns:
        Tupla (response, status_code)
    """
    response = {
        "success": False,
        "error": {
            "message": message,
            "code": error_code or f"ERROR_{status_code}",
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    return jsonify(response), status_code

def validation_error_response(
    errors: Dict[str, Any],
    message: str = "Datos de entrada no válidos"
) -> tuple:
    """
    Crear respuesta de error de validación
    
    Args:
        errors: Errores de validación
        message: Mensaje principal
    
    Returns:
        Tupla (response, status_code)
    """
    return error_response(
        message=message,
        status_code=400,
        error_code="VALIDATION_ERROR",
        details={"validation_errors": errors}
    )

def not_found_response(
    resource: str = "Recurso",
    message: Optional[str] = None
) -> tuple:
    """
    Crear respuesta de recurso no encontrado
    
    Args:
        resource: Nombre del recurso
        message: Mensaje personalizado
    
    Returns:
        Tupla (response, status_code)
    """
    if not message:
        message = f"{resource} no encontrado"
    
    return error_response(
        message=message,
        status_code=404,
        error_code="NOT_FOUND"
    )

def unauthorized_response(
    message: str = "No autorizado"
) -> tuple:
    """
    Crear respuesta de no autorizado
    
    Args:
        message: Mensaje de error
    
    Returns:
        Tupla (response, status_code)
    """
    return error_response(
        message=message,
        status_code=401,
        error_code="UNAUTHORIZED"
    )

def forbidden_response(
    message: str = "Acceso denegado"
) -> tuple:
    """
    Crear respuesta de acceso denegado
    
    Args:
        message: Mensaje de error
    
    Returns:
        Tupla (response, status_code)
    """
    return error_response(
        message=message,
        status_code=403,
        error_code="FORBIDDEN"
    )

def conflict_response(
    message: str = "Conflicto de datos"
) -> tuple:
    """
    Crear respuesta de conflicto
    
    Args:
        message: Mensaje de error
    
    Returns:
        Tupla (response, status_code)
    """
    return error_response(
        message=message,
        status_code=409,
        error_code="CONFLICT"
    )

def server_error_response(
    message: str = "Error interno del servidor"
) -> tuple:
    """
    Crear respuesta de error del servidor
    
    Args:
        message: Mensaje de error
    
    Returns:
        Tupla (response, status_code)
    """
    return error_response(
        message=message,
        status_code=500,
        error_code="INTERNAL_SERVER_ERROR"
    )

def paginated_response(
    data: list,
    page: int,
    per_page: int,
    total: int,
    message: str = "Datos obtenidos exitosamente"
) -> tuple:
    """
    Crear respuesta paginada
    
    Args:
        data: Lista de datos
        page: Página actual
        per_page: Elementos por página
        total: Total de elementos
        message: Mensaje de éxito
    
    Returns:
        Tupla (response, status_code)
    """
    total_pages = (total + per_page - 1) // per_page
    
    pagination = {
        "page": page,
        "per_page": per_page,
        "total": total,
        "pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1
    }
    
    return success_response(
        data={
            "items": data,
            "pagination": pagination
        },
        message=message
    )

def created_response(
    data: Any,
    message: str = "Recurso creado exitosamente"
) -> tuple:
    """
    Crear respuesta de recurso creado
    
    Args:
        data: Datos del recurso creado
        message: Mensaje de éxito
    
    Returns:
        Tupla (response, status_code)
    """
    return success_response(
        data=data,
        message=message,
        status_code=201
    )

def updated_response(
    data: Any,
    message: str = "Recurso actualizado exitosamente"
) -> tuple:
    """
    Crear respuesta de recurso actualizado
    
    Args:
        data: Datos del recurso actualizado
        message: Mensaje de éxito
    
    Returns:
        Tupla (response, status_code)
    """
    return success_response(
        data=data,
        message=message,
        status_code=200
    )

def deleted_response(
    message: str = "Recurso eliminado exitosamente"
) -> tuple:
    """
    Crear respuesta de recurso eliminado
    
    Args:
        message: Mensaje de éxito
    
    Returns:
        Tupla (response, status_code)
    """
    return success_response(
        data=None,
        message=message,
        status_code=200
    )
