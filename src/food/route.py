from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity

from libs.helpers import ApiResponse, CustomException, role_required, error_response_handler
from libs.enums import UserRolesEnum, ErrorTypesEnum

from src.food.schemas.add_food_item_schema import AddFoodItemSchema
from src.food.schemas.update_food_item_schema import UpdateFoodItemSchema
from src.food.service import FoodService

food_service = FoodService()

add_food_item_schema = AddFoodItemSchema()
update_food_item_schema = UpdateFoodItemSchema()

food_bp = Blueprint('food', __name__, url_prefix='/food')


@food_bp.route('/', methods=['POST'])
@jwt_required()
@role_required([UserRolesEnum.MERCHANT.value])
def add_food_item():
    try:

        merchant = get_jwt_identity()

        data = add_food_item_schema.load(request.form)

        if 'food_image' not in request.files:
            print(f'add_food_item - failed : no food_image')
            raise CustomException(400, "Please add food image!", ErrorTypesEnum.BAD_REQUEST_ERROR.value)

        food_image = request.files['food_image']

        if food_image.filename == '':
            print(f'add_food_item - failed : no selected food_image')
            raise CustomException(400, "No selected food image!", ErrorTypesEnum.BAD_REQUEST_ERROR.value)

        result = food_service.add_food_item(merchant["_id"], data, food_image)

        return ApiResponse.success_response(201, 'Food item added successful', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@food_bp.route('/merchant/<merchant_id>', methods=['GET'])
@jwt_required()
@role_required([UserRolesEnum.MERCHANT.value, UserRolesEnum.USER.value])
def get_food_items(merchant_id: str):
    try:

        result = food_service.get_food_items(merchant_id)

        return ApiResponse.success_response(200, 'Food items fetched successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@food_bp.route('/<food_id>', methods=['PUT'])
@jwt_required()
@role_required([UserRolesEnum.MERCHANT.value])
def update_food_item(food_id: str):
    try:

        data = update_food_item_schema.load(request.get_json())

        result = food_service.update_food_item(food_id, data)

        return ApiResponse.success_response(200, 'Food item updated successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@food_bp.route('/<food_id>', methods=['DELETE'])
@jwt_required()
@role_required([UserRolesEnum.MERCHANT.value])
def delete_food_item(food_id: str):
    try:

        food_service.delete_food_item(food_id)

        return ApiResponse.success_response(200, 'Food item deleted successfully', None)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)
