from marshmallow import Schema, fields, validate
from libs.enums import OrderPaymentMethodEnum


class CreateOrderSchema(Schema):
    delivery_address = fields.Str(required=True, validate=validate.Length(min=1))
    payment_method = fields.Str(required=True, validate=validate.OneOf(
        choices=[OrderPaymentMethodEnum.CASH_ON_DELIVERY.value, OrderPaymentMethodEnum.CARD_ON_DELIVERY.value]))
    latitude = fields.Float(required=True)
    longitude = fields.Float(required=True)
