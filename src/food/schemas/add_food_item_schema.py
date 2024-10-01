from marshmallow import Schema, fields, validate

from libs.enums import CuisineTypeEnum


class AddFoodItemSchema(Schema):
    cuisine_type = fields.Str(required=True,
                              validate=validate.OneOf(choices=[cuisine.value for cuisine in CuisineTypeEnum]))
    item_name = fields.Str(required=True, validate=validate.Length(min=1))
    price = fields.Number(required=True, validate=[validate.Range(min=0)])
    is_available = fields.Boolean(required=True)
    allergens = fields.Str(required=False)
