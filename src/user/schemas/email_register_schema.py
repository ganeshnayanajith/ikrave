from marshmallow import Schema, fields, validate

from src.user.schemas.preference_schema import PreferenceSchema


class EmailRegisterSchema(Schema):
    full_name = fields.Str(required=True, validate=validate.Length(min=1))
    username = fields.Str(required=True, validate=validate.Length(min=1))
    email = fields.Email(required=True, validate=validate.Length(min=6))
    password = fields.Str(required=True, validate=validate.Length(min=6))
    phone_number = fields.Str(required=True)
    address = fields.Str(required=True, validate=validate.Length(min=1))
    device_token = fields.Str(required=True)
    preferences = fields.List(fields.Nested(PreferenceSchema), required=True)
