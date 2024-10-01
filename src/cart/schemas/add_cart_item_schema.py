from marshmallow import Schema, fields, validate


class AddCartItemSchema(Schema):
    merchant_id = fields.Str(required=True, validate=validate.Length(min=1))
    food_id = fields.Str(required=True, validate=validate.Length(min=1))
