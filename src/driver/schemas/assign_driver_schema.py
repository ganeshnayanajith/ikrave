from marshmallow import Schema, fields, validate


class AssignDriverSchema(Schema):
    user_id = fields.Str(required=True, validate=validate.Length(min=1))
    order_id = fields.Str(required=True, validate=validate.Length(min=1))
    driver_id = fields.Str(required=True, validate=validate.Length(min=1))
