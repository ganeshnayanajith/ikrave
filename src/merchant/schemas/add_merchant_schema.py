from marshmallow import Schema, fields, validate


class AddMerchantSchema(Schema):
    request_id = fields.Str(required=True, validate=validate.Length(min=1))
