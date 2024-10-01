from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity

from libs.helpers import ApiResponse, CustomException, role_required, error_response_handler
from libs.enums import UserRolesEnum

from src.food_recommendation_engine.service import FoodRecommendationEngineService
from src.food_recommendation_engine.schemas.get_recommendations_by_food_name_schema import \
    GetRecommendationsByFoodNameSchema
from src.food_recommendation_engine.schemas.get_recommendations_by_cuisine_type_schema import \
    GetRecommendationsByCuisineTypeSchema

food_recommendation_engine_service = FoodRecommendationEngineService()

get_recommendations_by_food_name_schema = GetRecommendationsByFoodNameSchema()
get_recommendations_by_cuisine_type_schema = GetRecommendationsByCuisineTypeSchema()

food_recommendation_engine_bp = Blueprint('food_recommendation_engine', __name__,
                                          url_prefix='/food_recommendation_engine')


@food_recommendation_engine_bp.route('/by_food', methods=['POST'])
@jwt_required()
@role_required([UserRolesEnum.USER.value])
def get_recommendations_by_food_name():
    try:

        data = get_recommendations_by_food_name_schema.load(request.get_json())

        result = food_recommendation_engine_service.get_recommendations_by_food_name(data["food_name"])

        return ApiResponse.success_response(200, 'Food recommendations retrieved successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@food_recommendation_engine_bp.route('/by_cuisine', methods=['POST'])
@jwt_required()
@role_required([UserRolesEnum.USER.value])
def get_recommendations_by_cuisine_type():
    try:

        data = get_recommendations_by_cuisine_type_schema.load(request.get_json())

        result = food_recommendation_engine_service.get_recommendations_by_cuisine_type(data["cuisine_type"])

        return ApiResponse.success_response(200, 'Food recommendations retrieved successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@food_recommendation_engine_bp.route('/<merchant_id>', methods=['GET'])
@jwt_required()
@role_required([UserRolesEnum.USER.value])
def get_recommendations_for_user(merchant_id: str):
    try:

        user = get_jwt_identity()

        result = food_recommendation_engine_service.get_recommendations_for_user(user["_id"], merchant_id)

        if len(result) == 0:
            return ApiResponse.success_response(200, 'No recommendations found!', result)

        return ApiResponse.success_response(200, 'Food recommendations retrieved successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)
