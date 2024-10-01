from marshmallow import Schema, fields, validate
from libs.enums import OrderStatusEnum


class UpdateMerchantOrderSchema(Schema):
    status = fields.Str(required=True, validate=validate.OneOf(
        choices=[OrderStatusEnum.ACCEPTED.value, OrderStatusEnum.REJECTED.value, OrderStatusEnum.PREPARING.value,
                 OrderStatusEnum.PICKEDUP.value]))
