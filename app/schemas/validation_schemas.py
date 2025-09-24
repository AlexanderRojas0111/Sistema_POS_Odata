"""
Esquemas de Validación - Sistema POS O'Data
===========================================
Validación robusta de datos de entrada usando Marshmallow
"""

from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from decimal import Decimal
import re
from datetime import datetime

class BaseSchema(Schema):
    """Schema base con validaciones comunes"""
    
    class Meta:
        strict = True

class ProductSchema(BaseSchema):
    """Validación para productos"""
    
    name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=100, error="El nombre debe tener entre 1 y 100 caracteres"),
            validate.Regexp(r'^[a-zA-Z0-9\s\-_áéíóúñÁÉÍÓÚÑ]+$', error="El nombre contiene caracteres no válidos")
        ]
    )
    
    sku = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=50, error="El SKU debe tener entre 1 y 50 caracteres"),
            validate.Regexp(r'^[A-Z0-9\-_]+$', error="El SKU solo puede contener letras mayúsculas, números, guiones y guiones bajos")
        ]
    )
    
    price = fields.Decimal(
        required=True,
        places=2,
        validate=[
            validate.Range(min=0, error="El precio debe ser mayor o igual a 0"),
            validate.Range(max=999999.99, error="El precio no puede exceder 999,999.99")
        ]
    )
    
    cost = fields.Decimal(
        required=False,
        places=2,
        validate=[
            validate.Range(min=0, error="El costo debe ser mayor o igual a 0"),
            validate.Range(max=999999.99, error="El costo no puede exceder 999,999.99")
        ]
    )
    
    stock = fields.Int(
        required=True,
        validate=[
            validate.Range(min=0, error="El stock no puede ser negativo"),
            validate.Range(max=999999, error="El stock no puede exceder 999,999")
        ]
    )
    
    category = fields.Str(
        required=True,
        validate=[
            validate.Length(min=1, max=50, error="La categoría debe tener entre 1 y 50 caracteres"),
            validate.OneOf(
                ['sencillas', 'especiales', 'bebidas', 'postres', 'complementos'],
                error="Categoría no válida"
            )
        ]
    )
    
    description = fields.Str(
        required=False,
        validate=validate.Length(max=500, error="La descripción no puede exceder 500 caracteres")
    )
    
    barcode = fields.Str(
        required=False,
        validate=[
            validate.Length(min=8, max=20, error="El código de barras debe tener entre 8 y 20 caracteres"),
            validate.Regexp(r'^[0-9]+$', error="El código de barras solo puede contener números")
        ]
    )
    
    is_active = fields.Bool(required=False, missing=True)
    
    @validates_schema
    def validate_price_cost(self, data, **kwargs):
        """Validar que el precio sea mayor al costo"""
        if 'price' in data and 'cost' in data and data['cost']:
            if data['price'] < data['cost']:
                raise ValidationError("El precio debe ser mayor o igual al costo", field_name="price")

class SaleSchema(BaseSchema):
    """Validación para ventas"""
    
    total = fields.Decimal(
        required=True,
        places=2,
        validate=[
            validate.Range(min=0.01, error="El total debe ser mayor a 0"),
            validate.Range(max=999999.99, error="El total no puede exceder 999,999.99")
        ]
    )
    
    payment_method = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['cash', 'card', 'transfer', 'qr', 'other'],
            error="Método de pago no válido"
        )
    )
    
    customer_name = fields.Str(
        required=False,
        validate=[
            validate.Length(min=1, max=100, error="El nombre del cliente debe tener entre 1 y 100 caracteres"),
            validate.Regexp(r'^[a-zA-Z\sáéíóúñÁÉÍÓÚÑ]+$', error="El nombre del cliente contiene caracteres no válidos")
        ]
    )
    
    user_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="ID de usuario no válido")
    )
    
    discount = fields.Decimal(
        required=False,
        places=2,
        validate=[
            validate.Range(min=0, error="El descuento no puede ser negativo"),
            validate.Range(max=100, error="El descuento no puede exceder 100%")
        ]
    )
    
    tax = fields.Decimal(
        required=False,
        places=2,
        validate=[
            validate.Range(min=0, error="El impuesto no puede ser negativo"),
            validate.Range(max=50, error="El impuesto no puede exceder 50%")
        ]
    )
    
    items = fields.List(
        fields.Dict(),
        required=True,
        validate=validate.Length(min=1, error="La venta debe tener al menos un producto")
    )

class SaleItemSchema(BaseSchema):
    """Validación para items de venta"""
    
    product_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="ID de producto no válido")
    )
    
    quantity = fields.Int(
        required=True,
        validate=[
            validate.Range(min=1, error="La cantidad debe ser mayor a 0"),
            validate.Range(max=999, error="La cantidad no puede exceder 999")
        ]
    )
    
    price = fields.Decimal(
        required=True,
        places=2,
        validate=[
            validate.Range(min=0.01, error="El precio debe ser mayor a 0"),
            validate.Range(max=999999.99, error="El precio no puede exceder 999,999.99")
        ]
    )

class UserSchema(BaseSchema):
    """Validación para usuarios"""
    
    username = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=50, error="El nombre de usuario debe tener entre 3 y 50 caracteres"),
            validate.Regexp(r'^[a-zA-Z0-9_]+$', error="El nombre de usuario solo puede contener letras, números y guiones bajos")
        ]
    )
    
    email = fields.Email(
        required=True,
        validate=validate.Length(max=100, error="El email no puede exceder 100 caracteres")
    )
    
    password = fields.Str(
        required=True,
        validate=[
            validate.Length(min=8, error="La contraseña debe tener al menos 8 caracteres"),
            validate.Regexp(
                r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]',
                error="La contraseña debe contener al menos una letra minúscula, una mayúscula, un número y un carácter especial"
            )
        ]
    )
    
    full_name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=2, max=100, error="El nombre completo debe tener entre 2 y 100 caracteres"),
            validate.Regexp(r'^[a-zA-Z\sáéíóúñÁÉÍÓÚÑ]+$', error="El nombre completo contiene caracteres no válidos")
        ]
    )
    
    role = fields.Str(
        required=True,
        validate=validate.OneOf(
            ['admin', 'manager', 'cashier', 'viewer'],
            error="Rol no válido"
        )
    )
    
    is_active = fields.Bool(required=False, missing=True)

class LoginSchema(BaseSchema):
    """Validación para login"""
    
    username = fields.Str(
        required=True,
        validate=validate.Length(min=1, error="El nombre de usuario es requerido")
    )
    
    password = fields.Str(
        required=True,
        validate=validate.Length(min=1, error="La contraseña es requerida")
    )

class ReportFilterSchema(BaseSchema):
    """Validación para filtros de reportes"""
    
    start_date = fields.Date(
        required=True,
        error_messages={'invalid': 'Fecha de inicio no válida'}
    )
    
    end_date = fields.Date(
        required=True,
        error_messages={'invalid': 'Fecha de fin no válida'}
    )
    
    category = fields.Str(
        required=False,
        validate=validate.OneOf(
            ['sencillas', 'especiales', 'bebidas', 'postres', 'complementos', 'all'],
            error="Categoría no válida"
        )
    )
    
    payment_method = fields.Str(
        required=False,
        validate=validate.OneOf(
            ['cash', 'card', 'transfer', 'qr', 'other', 'all'],
            error="Método de pago no válido"
        )
    )
    
    user_id = fields.Int(
        required=False,
        validate=validate.Range(min=1, error="ID de usuario no válido")
    )
    
    @validates_schema
    def validate_date_range(self, data, **kwargs):
        """Validar que la fecha de inicio sea anterior a la fecha de fin"""
        if 'start_date' in data and 'end_date' in data:
            if data['start_date'] > data['end_date']:
                raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin", field_name="start_date")
            
            # Validar que el rango no exceda 1 año
            days_diff = (data['end_date'] - data['start_date']).days
            if days_diff > 365:
                raise ValidationError("El rango de fechas no puede exceder 1 año", field_name="end_date")

class PaginationSchema(BaseSchema):
    """Validación para paginación"""
    
    page = fields.Int(
        required=False,
        missing=1,
        validate=validate.Range(min=1, max=1000, error="La página debe estar entre 1 y 1000")
    )
    
    per_page = fields.Int(
        required=False,
        missing=20,
        validate=validate.OneOf([10, 20, 50, 100], error="Elementos por página no válido")
    )
    
    sort_by = fields.Str(
        required=False,
        validate=validate.Length(max=50, error="Campo de ordenamiento no válido")
    )
    
    sort_order = fields.Str(
        required=False,
        missing='asc',
        validate=validate.OneOf(['asc', 'desc'], error="Orden de clasificación no válido")
    )

class AISearchSchema(Schema):
    """Esquema para búsqueda semántica de IA"""
    query = fields.Str(
        required=True,
        validate=[
            validate.Length(min=2, max=200, error="Query must be between 2 and 200 characters"),
            validate.Regexp(r'^[a-zA-Z0-9\s\-_.,!?áéíóúñü]+$', error="Query contains invalid characters")
        ]
    )
    limit = fields.Int(
        missing=10,
        validate=validate.Range(min=1, max=50, error="Limit must be between 1 and 50")
    )
    filters = fields.Dict(missing={})

class AIRecommendationSchema(Schema):
    """Esquema para recomendaciones de IA"""
    product_id = fields.Int(
        required=True,
        validate=validate.Range(min=1, error="Product ID must be positive")
    )
    limit = fields.Int(
        missing=5,
        validate=validate.Range(min=1, max=20, error="Limit must be between 1 and 20")
    )
    algorithm = fields.Str(
        missing='collaborative',
        validate=validate.OneOf(['collaborative', 'content_based', 'hybrid'])
    )

class AISuggestionSchema(Schema):
    """Esquema para sugerencias de búsqueda"""
    query = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100, error="Query must be between 1 and 100 characters")
    )
    limit = fields.Int(
        missing=10,
        validate=validate.Range(min=1, max=20, error="Limit must be between 1 and 20")
    )

# Instancias de esquemas para uso en la aplicación
product_schema = ProductSchema()
sale_schema = SaleSchema()
sale_item_schema = SaleItemSchema()
user_schema = UserSchema()
login_schema = LoginSchema()
report_filter_schema = ReportFilterSchema()
pagination_schema = PaginationSchema()
ai_search_schema = AISearchSchema()
ai_recommendation_schema = AIRecommendationSchema()
ai_suggestion_schema = AISuggestionSchema()
