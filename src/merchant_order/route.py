from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity

from libs.enums import UserRolesEnum
from libs.helpers import ApiResponse, CustomException, role_required, error_response_handler

from src.merchant_order.service import MerchantOrderService
from src.merchant_order.schemas.update_merchant_order_schema import UpdateMerchantOrderSchema

merchant_order_service = MerchantOrderService()

update_merchant_order_schema = UpdateMerchantOrderSchema()

merchant_order_bp = Blueprint('merchant_order', __name__, url_prefix='/merchant_order')


@merchant_order_bp.route('/', methods=['GET'])
@jwt_required()
@role_required([UserRolesEnum.MERCHANT.value])
def get_merchant_orders():
    try:

        merchant = get_jwt_identity()

        status = request.args.get('status')

        result = merchant_order_service.get_merchant_orders_by_merchant_id(merchant["_id"], status)

        return ApiResponse.success_response(200, 'Merchant orders fetched successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@merchant_order_bp.route('/<merchant_order_id>', methods=['GET'])
@jwt_required()
@role_required([UserRolesEnum.MERCHANT.value])
def get_merchant_order(merchant_order_id: str):
    try:

        merchant = get_jwt_identity()

        result = merchant_order_service.get_merchant_order_by_merchant_id_and_order_id(merchant["_id"],
                                                                                       merchant_order_id)

        return ApiResponse.success_response(200, 'Merchant order details fetched successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@merchant_order_bp.route('/<order_id>/<merchant_order_id>', methods=['PUT'])
@jwt_required()
@role_required([UserRolesEnum.MERCHANT.value])
def update_merchant_order(order_id: str, merchant_order_id: str):
    try:

        merchant = get_jwt_identity()

        data = update_merchant_order_schema.load(request.get_json())

        result = merchant_order_service.update_merchant_order(merchant["_id"], order_id, merchant_order_id, data)

        return ApiResponse.success_response(200, 'Merchant order details updated successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)
