from marshmallow import Schema, fields, validate


class GetNearbyMerchantSchema(Schema):
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
