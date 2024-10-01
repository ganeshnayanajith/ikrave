from marshmallow import Schema, fields


class VerifyEmailSchema(Schema):
    verification_code = fields.Number(required=True)
