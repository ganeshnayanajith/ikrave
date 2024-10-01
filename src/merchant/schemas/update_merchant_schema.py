from marshmallow import Schema, fields, validate


class UpdateMerchantSchema(Schema):
    name = fields.Str(required=False, validate=validate.Length(min=1))
    address = fields.Str(required=False, validate=validate.Length(min=1))
    phone_number = fields.Str(required=False, validate=validate.Length(min=1))
    is_available = fields.Boolean(required=False)
