from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from libs.helpers import ApiResponse, CustomException, role_required, error_response_handler
from libs.enums import UserRolesEnum
from marshmallow import ValidationError

from src.cart.schemas.remove_cart_item_schema import RemoveCartItemSchema
from src.cart.service import CartService
from src.cart.schemas.add_cart_item_schema import AddCartItemSchema

cart_service = CartService()
add_cart_item_schema = AddCartItemSchema()
remove_cart_item_schema = RemoveCartItemSchema()

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')


@cart_bp.route('/', methods=['POST'])
@jwt_required()
@role_required([UserRolesEnum.USER.value])
def add_cart_item():
    try:
        user = get_jwt_identity()
        data = add_cart_item_schema.load(request.get_json())

        result = cart_service.add_cart_item(user["_id"], data)

        return ApiResponse.success_response(200, 'Card item added successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@cart_bp.route('/', methods=['DELETE'])
@jwt_required()
@role_required([UserRolesEnum.USER.value])
def remove_cart_item():
    try:
        user = get_jwt_identity()
        data = remove_cart_item_schema.load(request.get_json())

        result = cart_service.remove_cart_item(user["_id"], data)

        return ApiResponse.success_response(200, 'Card item removed successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@cart_bp.route('/', methods=['GET'])
@jwt_required()
@role_required([UserRolesEnum.USER.value])
def get_cart_items():
    try:
        user = get_jwt_identity()

        result = cart_service.get_cart_items(user["_id"])

        return ApiResponse.success_response(200, 'Card items fetched successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@cart_bp.route('/clear', methods=['DELETE'])
@jwt_required()
@role_required([UserRolesEnum.USER.value])
def clear_cart():
    try:
        user = get_jwt_identity()

        result = cart_service.clear_cart(user["_id"])

        return ApiResponse.success_response(200, 'Card cleared successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)
