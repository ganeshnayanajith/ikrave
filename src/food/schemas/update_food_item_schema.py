from marshmallow import Schema, fields, validate


class UpdateFoodItemSchema(Schema):
    item_name = fields.Str(required=False, validate=validate.Length(min=1))
    price = fields.Number(required=False, validate=[validate.Range(min=0)])
    is_available = fields.Boolean(required=False)
    rating = fields.Number(required=False, validate=[validate.Range(min=0)])
