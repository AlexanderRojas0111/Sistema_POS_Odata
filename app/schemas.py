"""
Esquemas de validación para el Sistema POS O'data
Usando Marshmallow para serialización/deserialización
Y Pydantic para validación de tipos
"""

from marshmallow import Schema, fields, validate, ValidationError
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# =============================================================================
# ESQUEMAS PYDANTIC (Para validación de tipos y entrada de datos)
# =============================================================================

class InventoryCreate(BaseModel):
    """Esquema Pydantic para crear inventario"""
    product_id: int = Field(..., gt=0, description="ID del producto")
    quantity: int = Field(..., gt=0, description="Cantidad a agregar/quitar")
    location: Optional[str] = Field(None, max_length=100, description="Ubicación del inventario")
    movement_type: str = Field(..., description="Tipo de movimiento: 'add', 'remove', 'adjust'")
    user_id: int = Field(..., gt=0, description="ID del usuario que realiza el movimiento")
    notes: Optional[str] = Field(None, max_length=500, description="Notas adicionales")

class InventoryUpdate(BaseModel):
    """Esquema Pydantic para actualizar inventario"""
    quantity: Optional[int] = Field(None, gt=0, description="Nueva cantidad")
    location: Optional[str] = Field(None, max_length=100, description="Nueva ubicación")
    movement_type: Optional[str] = Field(None, description="Nuevo tipo de movimiento")
    notes: Optional[str] = Field(None, max_length=500, description="Nuevas notas")

class ProductCreate(BaseModel):
    """Esquema Pydantic para crear productos"""
    name: str = Field(..., min_length=1, max_length=100, description="Nombre del producto")
    description: Optional[str] = Field(None, max_length=500, description="Descripción del producto")
    price: float = Field(..., gt=0, description="Precio del producto")
    category: Optional[str] = Field(None, max_length=50, description="Categoría del producto")
    stock: Optional[int] = Field(0, ge=0, description="Stock inicial")
    barcode: Optional[str] = Field(None, max_length=50, description="Código de barras")

class ProductUpdate(BaseModel):
    """Esquema Pydantic para actualizar productos"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    category: Optional[str] = Field(None, max_length=50)
    stock: Optional[int] = Field(None, ge=0)
    barcode: Optional[str] = Field(None, max_length=50)

class UserCreate(BaseModel):
    """Esquema Pydantic para crear usuarios"""
    username: str = Field(..., min_length=3, max_length=50, description="Nombre de usuario")
    email: str = Field(..., description="Email del usuario")
    password: str = Field(..., min_length=6, description="Contraseña")
    role: str = Field(..., description="Rol del usuario: ADMIN, MANAGER, EMPLOYEE")
    is_active: Optional[bool] = Field(True, description="Estado activo del usuario")

class UserUpdate(BaseModel):
    """Esquema Pydantic para actualizar usuarios"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, description="Email del usuario")
    role: Optional[str] = Field(None, description="Rol del usuario")
    is_active: Optional[bool] = Field(None, description="Estado activo")

class SaleCreate(BaseModel):
    """Esquema Pydantic para crear ventas"""
    products: List[Dict[str, Any]] = Field(..., description="Lista de productos con cantidad")
    customer_name: Optional[str] = Field(None, max_length=100, description="Nombre del cliente")
    payment_method: Optional[str] = Field("Efectivo", max_length=50, description="Método de pago")

class LoginRequest(BaseModel):
    """Esquema Pydantic para login"""
    username: str = Field(..., description="Nombre de usuario")
    password: str = Field(..., description="Contraseña")

class ChangePasswordRequest(BaseModel):
    """Esquema Pydantic para cambiar contraseña"""
    current_password: str = Field(..., description="Contraseña actual")
    new_password: str = Field(..., min_length=6, description="Nueva contraseña")

# =============================================================================
# ESQUEMAS MARSHMALLOW (Para serialización/deserialización de respuestas)
# =============================================================================

class ProductSchema(Schema):
    """Esquema Marshmallow para productos"""
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    price = fields.Float(required=True, validate=validate.Range(min=0))
    stock = fields.Int(validate=validate.Range(min=0))
    category = fields.Str(validate=validate.Length(max=50))
    barcode = fields.Str(validate=validate.Length(max=50))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class SaleItemSchema(Schema):
    """Esquema Marshmallow para items de venta"""
    id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True, validate=validate.Range(min=1))
    quantity = fields.Int(required=True, validate=validate.Range(min=1))
    unit_price = fields.Float(required=True, validate=validate.Range(min=0))
    subtotal = fields.Float(dump_only=True)

class SaleSchema(Schema):
    """Esquema Marshmallow para ventas"""
    id = fields.Int(dump_only=True)
    user_id = fields.Int(dump_only=True)
    customer_name = fields.Str(validate=validate.Length(max=100))
    total_amount = fields.Float(dump_only=True)
    payment_method = fields.Str(validate=validate.Length(max=50))
    sale_date = fields.DateTime(dump_only=True)
    items = fields.Nested(SaleItemSchema, many=True)

class UserSchema(Schema):
    """Esquema Marshmallow para usuarios"""
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    role = fields.Str(validate=validate.OneOf(['ADMIN', 'MANAGER', 'EMPLOYEE']))
    is_active = fields.Bool(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class LoginSchema(Schema):
    """Esquema Marshmallow para login"""
    username = fields.Str(required=True)
    password = fields.Str(required=True)

class CreateUserSchema(Schema):
    """Esquema Marshmallow para crear usuarios"""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    role = fields.Str(required=True, validate=validate.OneOf(['ADMIN', 'MANAGER', 'EMPLOYEE']))

class ChangePasswordSchema(Schema):
    """Esquema Marshmallow para cambiar contraseña"""
    current_password = fields.Str(required=True)
    new_password = fields.Str(required=True, validate=validate.Length(min=6))

class CreateSaleSchema(Schema):
    """Esquema Marshmallow para crear ventas"""
    products = fields.List(fields.Dict(), required=True)
    customer_name = fields.Str(validate=validate.Length(max=100))
    payment_method = fields.Str(validate=validate.Length(max=50))

class ProductUpdateSchema(Schema):
    """Esquema Marshmallow para actualizar productos"""
    name = fields.Str(validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    price = fields.Float(validate=validate.Range(min=0))
    stock = fields.Int(validate=validate.Range(min=0))
    category = fields.Str(validate=validate.Length(max=50))
    barcode = fields.Str(validate=validate.Length(max=50))

class UserUpdateSchema(Schema):
    """Esquema Marshmallow para actualizar usuarios"""
    username = fields.Str(validate=validate.Length(min=3, max=50))
    email = fields.Email()
    role = fields.Str(validate=validate.OneOf(['ADMIN', 'MANAGER', 'EMPLOYEE']))
    is_active = fields.Bool()

class InventorySchema(Schema):
    """Esquema Marshmallow para inventario"""
    id = fields.Int(dump_only=True)
    product_id = fields.Int(required=True, validate=validate.Range(min=1))
    quantity = fields.Int(required=True, validate=validate.Range(min=0))
    location = fields.Str(validate=validate.Length(max=100))
    movement_type = fields.Str(required=True, validate=validate.OneOf(['add', 'remove', 'adjust']))
    user_id = fields.Int(required=True, validate=validate.Range(min=1))
    notes = fields.Str(validate=validate.Length(max=500))
    created_at = fields.DateTime(dump_only=True)

# =============================================================================
# ESQUEMAS PARA RESPUESTAS DE API
# =============================================================================

class ProductResponseSchema(Schema):
    """Esquema de respuesta para productos"""
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    price = fields.Float()
    stock = fields.Int()
    category = fields.Str()
    barcode = fields.Str()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

class SaleResponseSchema(Schema):
    """Esquema de respuesta para ventas"""
    id = fields.Int()
    user_id = fields.Int()
    customer_name = fields.Str()
    total_amount = fields.Float()
    payment_method = fields.Str()
    sale_date = fields.DateTime()
    items = fields.Nested(SaleItemSchema, many=True)

class UserResponseSchema(Schema):
    """Esquema de respuesta para usuarios"""
    id = fields.Int()
    username = fields.Str()
    email = fields.Str()
    role = fields.Str()
    is_active = fields.Bool()
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

class LoginResponseSchema(Schema):
    """Esquema de respuesta para login"""
    access_token = fields.Str()
    refresh_token = fields.Str()
    user = fields.Nested(UserResponseSchema)

class ErrorResponseSchema(Schema):
    """Esquema de respuesta para errores"""
    error = fields.Str()
    message = fields.Str()
    details = fields.Dict()

class SuccessResponseSchema(Schema):
    """Esquema de respuesta para éxito"""
    message = fields.Str()
    data = fields.Dict()

class PaginationSchema(Schema):
    """Esquema para paginación"""
    total = fields.Int()
    pages = fields.Int()
    current_page = fields.Int()
    per_page = fields.Int()

class ProductsListResponseSchema(Schema):
    """Esquema de respuesta para lista de productos"""
    products = fields.Nested(ProductResponseSchema, many=True)
    total = fields.Int()
    pages = fields.Int()
    current_page = fields.Int()

class SalesListResponseSchema(Schema):
    """Esquema de respuesta para lista de ventas"""
    sales = fields.Nested(SaleResponseSchema, many=True)
    total = fields.Int()
    pages = fields.Int()
    current_page = fields.Int()

class UsersListResponseSchema(Schema):
    """Esquema de respuesta para lista de usuarios"""
    users = fields.Nested(UserResponseSchema, many=True)
    total = fields.Int()
    pages = fields.Int()
    current_page = fields.Int()

class InventoryResponseSchema(Schema):
    """Esquema de respuesta para inventario"""
    id = fields.Int()
    product_id = fields.Int()
    quantity = fields.Int()
    location = fields.Str()
    movement_type = fields.Str()
    user_id = fields.Int()
    notes = fields.Str()
    created_at = fields.DateTime()

class InventoryResponse(BaseModel):
    """Esquema Pydantic de respuesta para inventario"""
    id: int
    product_id: int
    quantity: int
    location: Optional[str]
    movement_type: str
    user_id: int
    notes: Optional[str]
    created_at: datetime

# =============================================================================
# EXPORTACIONES PARA FACILITAR IMPORTS
# =============================================================================

__all__ = [
    # Pydantic schemas
    'InventoryCreate', 'InventoryUpdate', 'ProductCreate', 'ProductUpdate', 'UserCreate', 'UserUpdate',
    'SaleCreate', 'LoginRequest', 'ChangePasswordRequest', 'InventoryResponse',
    
    # Marshmallow schemas
    'ProductSchema', 'SaleItemSchema', 'SaleSchema', 'UserSchema', 'LoginSchema',
    'CreateUserSchema', 'ChangePasswordSchema', 'CreateSaleSchema', 'ProductUpdateSchema',
    'UserUpdateSchema', 'InventorySchema',
    
    # Response schemas
    'ProductResponseSchema', 'SaleResponseSchema', 'UserResponseSchema',
    'LoginResponseSchema', 'ErrorResponseSchema', 'SuccessResponseSchema',
    'PaginationSchema', 'ProductsListResponseSchema', 'SalesListResponseSchema',
    'UsersListResponseSchema', 'InventoryResponseSchema'
]
