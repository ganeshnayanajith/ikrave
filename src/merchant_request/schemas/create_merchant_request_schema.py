from marshmallow import Schema, fields, validate


class CreateMerchantRequestSchema(Schema):
    username = fields.Str(required=True, validate=validate.Length(min=1))
    business_name = fields.Str(required=True, validate=validate.Length(min=1))
    business_registration = fields.Str(required=True, validate=validate.Length(min=1))
    food_hygiene_rating = fields.Float(required=True)
    business_address = fields.Str(required=True, validate=validate.Length(min=1))
    phone_number = fields.Str(required=True, validate=validate.Length(min=1))
    opening_hours = fields.Str(required=True, validate=validate.Length(min=1))
    closing_hours = fields.Str(required=True, validate=validate.Length(min=1))
    geo_location = fields.Str(required=True, validate=validate.Length(min=1))
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
