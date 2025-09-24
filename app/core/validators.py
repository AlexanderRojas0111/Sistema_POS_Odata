"""
Sistema de Validación Empresarial
Validación robusta y estandarizada de datos de entrada
"""

import re
import logging
from typing import Any, Dict, List, Optional, Union, Callable
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from marshmallow import Schema, fields, validate, ValidationError, post_load
from app.core.exceptions import ValidationException

logger = logging.getLogger(__name__)

class BaseValidator:
    """Validador base con funcionalidades comunes"""
    
    @staticmethod
    def is_empty(value: Any) -> bool:
        """Verificar si un valor está vacío"""
        if value is None:
            return True
        if isinstance(value, str) and value.strip() == "":
            return True
        if isinstance(value, (list, dict)) and len(value) == 0:
            return True
        return False
    
    @staticmethod
    def sanitize_string(value: str) -> str:
        """Sanitizar string de entrada"""
        if not isinstance(value, str):
            return str(value)
        
        # Remover caracteres peligrosos
        value = re.sub(r'[<>"\']', '', value)
        # Normalizar espacios
        value = re.sub(r'\s+', ' ', value.strip())
        return value
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validar formato de email"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validar formato de teléfono"""
        # Formato: +57 300 123 4567 o 3001234567
        pattern = r'^(\+\d{1,3}\s?)?\d{3}\s?\d{3}\s?\d{4}$'
        return re.match(pattern, phone.replace('-', ' ')) is not None

class SecurityValidator:
    """Validador de seguridad para prevenir ataques"""
    
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC)\b)",
        r"(\b(UNION|OR|AND)\b.*=)",
        r"(['\"];?\s*(DROP|DELETE|INSERT|UPDATE))",
        r"(\b(SCRIPT|JAVASCRIPT|VBSCRIPT)\b)",
    ]
    
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>.*?</iframe>",
    ]
    
    @classmethod
    def check_sql_injection(cls, value: str) -> bool:
        """Detectar intentos de inyección SQL"""
        if not isinstance(value, str):
            return False
        
        value_upper = value.upper()
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                logger.warning(f"SQL injection attempt detected: {value}")
                return True
        return False
    
    @classmethod
    def check_xss(cls, value: str) -> bool:
        """Detectar intentos de XSS"""
        if not isinstance(value, str):
            return False
        
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                logger.warning(f"XSS attempt detected: {value}")
                return True
        return False
    
    @classmethod
    def validate_safe_input(cls, value: str, field_name: str = "input") -> str:
        """Validar que la entrada sea segura"""
        if cls.check_sql_injection(value):
            raise ValidationException(
                f"Contenido potencialmente peligroso detectado en {field_name}",
                field=field_name,
                value=value
            )
        
        if cls.check_xss(value):
            raise ValidationException(
                f"Contenido potencialmente peligroso detectado en {field_name}",
                field=field_name,
                value=value
            )
        
        return BaseValidator.sanitize_string(value)

# Campos personalizados de Marshmallow
class SafeString(fields.String):
    """Campo string con validación de seguridad"""
    
    def _deserialize(self, value, attr, obj, **kwargs):
        value = super()._deserialize(value, attr, obj, **kwargs)
        if value:
            return SecurityValidator.validate_safe_input(value, attr)
        return value

class MoneyField(fields.Decimal):
    """Campo para valores monetarios"""
    
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('places', 2)
        kwargs.setdefault('rounding', None)
        super().__init__(*args, **kwargs)
    
    def _deserialize(self, value, attr, obj, **kwargs):
        if isinstance(value, str):
            # Remover símbolos de moneda y espacios
            value = re.sub(r'[^\d.,\-]', '', value)
            # Normalizar separadores decimales
            value = value.replace(',', '.')
        
        try:
            result = super()._deserialize(value, attr, obj, **kwargs)
            if result < 0:
                raise ValidationError("El valor monetario no puede ser negativo")
            return result
        except (ValueError, InvalidOperation):
            raise ValidationError("Formato de valor monetario inválido")

class StockField(fields.Integer):
    """Campo para cantidades de stock"""
    
    def _deserialize(self, value, attr, obj, **kwargs):
        result = super()._deserialize(value, attr, obj, **kwargs)
        if result < 0:
            raise ValidationError("La cantidad en stock no puede ser negativa")
        return result

# Esquemas de validación para entidades principales
class UserValidationSchema(Schema):
    """Esquema de validación para usuarios"""
    
    username = SafeString(
        required=True,
        validate=[
            validate.Length(min=3, max=50),
            validate.Regexp(r'^[a-zA-Z0-9_]+$', error="Solo letras, números y guiones bajos")
        ]
    )
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        validate=validate.Length(min=8, max=128),
        load_only=True
    )
    full_name = SafeString(
        required=True,
        validate=validate.Length(min=2, max=100)
    )
    phone = fields.String(
        validate=validate.Length(max=20),
        allow_none=True
    )
    role = fields.String(
        required=True,
        validate=validate.OneOf(['admin', 'manager', 'employee'])
    )
    is_active = fields.Boolean(default=True)
    
    @post_load
    def validate_phone_format(self, data, **kwargs):
        if data.get('phone') and not BaseValidator.validate_phone(data['phone']):
            raise ValidationError({'phone': 'Formato de teléfono inválido'})
        return data

class ProductValidationSchema(Schema):
    """Esquema de validación para productos"""
    
    name = SafeString(
        required=True,
        validate=validate.Length(min=1, max=200)
    )
    description = SafeString(
        validate=validate.Length(max=1000),
        allow_none=True
    )
    sku = SafeString(
        required=True,
        validate=[
            validate.Length(min=1, max=50),
            validate.Regexp(r'^[A-Z0-9-_]+$', error="SKU debe contener solo letras mayúsculas, números, guiones y guiones bajos")
        ]
    )
    barcode = SafeString(
        validate=validate.Length(max=50),
        allow_none=True
    )
    price = MoneyField(required=True)
    cost = MoneyField(allow_none=True)
    category_id = fields.Integer(allow_none=True)
    supplier_id = fields.Integer(allow_none=True)
    min_stock = StockField(default=0)
    max_stock = StockField(allow_none=True)
    is_active = fields.Boolean(default=True)
    
    @post_load
    def validate_stock_levels(self, data, **kwargs):
        min_stock = data.get('min_stock', 0)
        max_stock = data.get('max_stock')
        
        if max_stock is not None and min_stock > max_stock:
            raise ValidationError({
                'max_stock': 'El stock máximo debe ser mayor al stock mínimo'
            })
        return data

class SaleValidationSchema(Schema):
    """Esquema de validación para ventas"""
    
    customer_id = fields.Integer(allow_none=True)
    items = fields.List(
        fields.Nested('SaleItemValidationSchema'),
        required=True,
        validate=validate.Length(min=1)
    )
    payment_method = SafeString(
        required=True,
        validate=validate.OneOf(['cash', 'card', 'transfer', 'credit'])
    )
    discount_amount = MoneyField(default=Decimal('0.00'))
    tax_amount = MoneyField(default=Decimal('0.00'))
    notes = SafeString(
        validate=validate.Length(max=500),
        allow_none=True
    )

class SaleItemValidationSchema(Schema):
    """Esquema de validación para items de venta"""
    
    product_id = fields.Integer(required=True)
    quantity = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )
    unit_price = MoneyField(required=True)
    discount_amount = MoneyField(default=Decimal('0.00'))

class InventoryValidationSchema(Schema):
    """Esquema de validación para movimientos de inventario"""
    
    product_id = fields.Integer(required=True)
    movement_type = SafeString(
        required=True,
        validate=validate.OneOf(['in', 'out', 'adjustment', 'transfer'])
    )
    quantity = fields.Integer(
        required=True,
        validate=validate.Range(min=1)
    )
    reference = SafeString(
        validate=validate.Length(max=100),
        allow_none=True
    )
    notes = SafeString(
        validate=validate.Length(max=500),
        allow_none=True
    )

# Validador de negocio
class BusinessValidator:
    """Validador de reglas de negocio"""
    
    @staticmethod
    def validate_sale_business_rules(sale_data: Dict[str, Any]) -> None:
        """Validar reglas de negocio para ventas"""
        
        # Validar que el total sea coherente
        items = sale_data.get('items', [])
        calculated_total = sum(
            Decimal(str(item['quantity'])) * Decimal(str(item['unit_price'])) - 
            Decimal(str(item.get('discount_amount', 0)))
            for item in items
        )
        
        discount = Decimal(str(sale_data.get('discount_amount', 0)))
        tax = Decimal(str(sale_data.get('tax_amount', 0)))
        expected_total = calculated_total - discount + tax
        
        # Validar que el descuento no sea mayor al subtotal
        if discount > calculated_total:
            raise ValidationException(
                "El descuento no puede ser mayor al subtotal de la venta",
                field="discount_amount"
            )
    
    @staticmethod
    def validate_inventory_business_rules(inventory_data: Dict[str, Any]) -> None:
        """Validar reglas de negocio para inventario"""
        
        movement_type = inventory_data.get('movement_type')
        quantity = inventory_data.get('quantity', 0)
        
        # Validar movimientos de salida
        if movement_type == 'out':
            # Aquí se validaría contra el stock actual
            # Esta validación se haría en el servicio con acceso a la DB
            pass

# Decorador para validación automática
def validate_json(schema_class: Schema):
    """Decorador para validación automática de JSON en endpoints"""
    
    def decorator(func):
        from functools import wraps
        from flask import request, jsonify
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                schema = schema_class()
                json_data = request.get_json()
                
                if json_data is None:
                    raise ValidationException("Se requiere contenido JSON válido")
                
                # Validar y deserializar
                validated_data = schema.load(json_data)
                
                # Pasar datos validados a la función
                return func(validated_data, *args, **kwargs)
                
            except ValidationError as e:
                raise ValidationException(
                    f"Errores de validación: {e.messages}",
                    details={'validation_errors': e.messages}
                )
        
        return wrapper
    return decorator

# Utilidades de validación
class ValidationUtils:
    """Utilidades para validación"""
    
    @staticmethod
    def validate_date_range(start_date: date, end_date: date) -> None:
        """Validar rango de fechas"""
        if start_date > end_date:
            raise ValidationException(
                "La fecha de inicio debe ser anterior a la fecha de fin"
            )
        
        if end_date > date.today():
            raise ValidationException(
                "La fecha de fin no puede ser futura"
            )
    
    @staticmethod
    def validate_pagination(page: int, per_page: int) -> None:
        """Validar parámetros de paginación"""
        if page < 1:
            raise ValidationException("El número de página debe ser mayor a 0")
        
        if per_page < 1 or per_page > 100:
            raise ValidationException(
                "El número de elementos por página debe estar entre 1 y 100"
            )
    
    @staticmethod
    def validate_search_query(query: str) -> str:
        """Validar y limpiar consulta de búsqueda"""
        if not query or len(query.strip()) < 2:
            raise ValidationException(
                "La consulta de búsqueda debe tener al menos 2 caracteres"
            )
        
        return SecurityValidator.validate_safe_input(query.strip(), "search_query")
