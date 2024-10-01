from marshmallow import Schema, fields, validate


class PreferenceSchema(Schema):
    question = fields.Str(required=True, validate=validate.Length(min=1))
    answer = fields.List(fields.Str(), required=True)
