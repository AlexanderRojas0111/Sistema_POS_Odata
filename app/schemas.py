from marshmallow import Schema, fields, validate
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Schemas de Pydantic para la API
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "EMPLOYEE"
    is_active: bool = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: str
    password: str

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    barcode: Optional[str] = None
    category: Optional[str] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    barcode: Optional[str] = None
    category: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    price: float
    barcode: Optional[str] = None
    category: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class InventoryCreate(BaseModel):
    product_id: int
    quantity: int
    movement_type: str
    user_id: int

class InventoryUpdate(BaseModel):
    quantity: Optional[int] = None
    movement_type: Optional[str] = None

class InventoryResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    movement_type: str
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SaleCreate(BaseModel):
    product_id: int
    quantity: int
    total: float
    user_id: int
    customer_id: Optional[int] = None

class SaleUpdate(BaseModel):
    quantity: Optional[int] = None
    total: Optional[float] = None
    customer_id: Optional[int] = None

class SaleResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    total: float
    user_id: int
    customer_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Schemas de Marshmallow (legacy)
class UserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    name = fields.Str(required=True, validate=validate.Length(min=1))

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))

class SaleSchema(Schema):
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True)
    total = fields.Float(required=True)
    user_id = fields.Int(required=True)

class InventorySchema(Schema):
    product_id = fields.Int(required=True)
    quantity = fields.Int(required=True)
    movement_type = fields.Str(required=True)
    user_id = fields.Int(required=True)
