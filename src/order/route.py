from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from libs.helpers import ApiResponse, CustomException, role_required, error_response_handler
from libs.enums import UserRolesEnum

from src.order.schemas.create_order_schema import CreateOrderSchema
from src.order.service import OrderService

order_service = OrderService()

create_order_schema = CreateOrderSchema()

order_bp = Blueprint('order', __name__, url_prefix='/order')


@order_bp.route('/', methods=['POST'])
@jwt_required()
@role_required([UserRolesEnum.USER.value])
def create_order():
    try:
        user = get_jwt_identity()

        data = create_order_schema.load(request.get_json())

        result = order_service.create_order(user["_id"], data)

        return ApiResponse.success_response(201, 'Order created successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@order_bp.route('/', methods=['GET'])
@jwt_required()
@role_required([UserRolesEnum.DRIVER.value, UserRolesEnum.USER.value])
def get_orders_by_user_id_and_type():
    try:
        user = get_jwt_identity()

        status_string = request.args.get('status')

        statuses = []

        if status_string:
            statuses = status_string.split(",")

        print(f'get_orders_by_user_id_and_type - statuses - {statuses}')

        result = order_service.get_orders_by_user_id_and_type(user["_id"], user["role"], statuses)

        return ApiResponse.success_response(200, 'Order details fetched successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@order_bp.route('/<order_id>', methods=['GET'])
@jwt_required()
@role_required([UserRolesEnum.USER.value])
def get_order(order_id: str):
    try:
        user = get_jwt_identity()

        result = order_service.get_order_by_user_id_and_order_id(user["_id"], order_id)

        return ApiResponse.success_response(200, 'Order details fetched successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@order_bp.route('/<order_id>', methods=['PUT'])
@jwt_required()
@role_required([UserRolesEnum.DRIVER.value])
def complete_order(order_id: str):
    try:
        driver = get_jwt_identity()

        result = order_service.complete_order(driver["_id"], order_id)

        return ApiResponse.success_response(200, 'Order completed successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)
