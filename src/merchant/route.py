from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity

from libs.enums import ErrorTypesEnum, UserRolesEnum
from libs.helpers import ApiResponse, CustomException, role_required, error_response_handler

from src.merchant.schemas.get_nearby_merchant_schema import GetNearbyMerchantSchema
from src.merchant.schemas.update_merchant_schema import UpdateMerchantSchema
from src.merchant_request.schemas.create_merchant_request_schema import CreateMerchantRequestSchema
from src.merchant.schemas.add_merchant_schema import AddMerchantSchema
from src.merchant.service import MerchantService
from src.user.schemas.login_schema import LoginSchema

merchant_service = MerchantService()

create_merchant_request_schema = CreateMerchantRequestSchema()
add_merchant_schema = AddMerchantSchema()
login_schema = LoginSchema()
update_merchant_schema = UpdateMerchantSchema()
get_nearby_merchant_schema = GetNearbyMerchantSchema()

merchant_bp = Blueprint('merchant', __name__, url_prefix='/merchant')


@merchant_bp.route('/', methods=['POST'])
@jwt_required()
@role_required([UserRolesEnum.ADMIN.value])
def add_merchant():
    try:
        admin = get_jwt_identity()
        data = add_merchant_schema.load(request.get_json())

        result = merchant_service.add_merchant(admin["_id"], data.get('request_id'))

        return ApiResponse.success_response(201, 'Merchant added successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@merchant_bp.route('/login', methods=['POST'])
def login():
    try:

        data = login_schema.load(request.get_json())

        result = merchant_service.login_merchant(data.get('username'), data.get('password'))

        return ApiResponse.success_response(200, 'Login successful', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@merchant_bp.route('/', methods=['GET'])
@jwt_required()
@role_required([UserRolesEnum.USER.value])
def get_merchants():
    try:

        result = merchant_service.get_merchants()

        return ApiResponse.success_response(200, 'Merchants fetched successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@merchant_bp.route('/nearby', methods=['POST'])
@jwt_required()
@role_required([UserRolesEnum.USER.value])
def get_nearby_merchants():
    try:

        data = get_nearby_merchant_schema.load(request.get_json())

        result = merchant_service.get_nearby_merchants(data.get('latitude'), data.get('longitude'))

        return ApiResponse.success_response(200, 'Nearby merchants fetched successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@merchant_bp.route('/', methods=['PUT'])
@jwt_required()
@role_required([UserRolesEnum.MERCHANT.value])
def update_merchant():
    try:

        merchant = get_jwt_identity()

        data = update_merchant_schema.load(request.get_json())

        result = merchant_service.update_merchant(merchant["_id"], data)

        return ApiResponse.success_response(200, 'Merchant updated successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)
