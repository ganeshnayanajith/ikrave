from marshmallow import Schema, fields, validate

from src.user.schemas.preference_schema import PreferenceSchema


class UpdateProfileSchema(Schema):
    address = fields.Str(required=True, validate=validate.Length(min=1))
    preferences = fields.List(fields.Nested(PreferenceSchema), required=True)
