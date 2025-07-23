from marshmallow import Schema, fields, validate


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
