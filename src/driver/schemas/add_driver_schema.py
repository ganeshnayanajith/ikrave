from marshmallow import Schema, fields, validate


class AddDriverSchema(Schema):
    full_name = fields.Str(required=True, validate=validate.Length(min=1))
    username = fields.Str(required=True, validate=validate.Length(min=1))
    password = fields.Str(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True, validate=validate.Length(min=6))
    phone_number = fields.Str(required=True, validate=validate.Length(min=1))
    licence = fields.Str(required=True, validate=validate.Length(min=1))
    vehicle_reg = fields.Str(required=True, validate=validate.Length(min=1))
