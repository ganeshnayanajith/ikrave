from marshmallow import ValidationError
from flask_jwt_extended import jwt_required
from flask import Blueprint, request

from libs.helpers import ApiResponse, CustomException, role_required, error_response_handler
from libs.enums import UserRolesEnum, ErrorTypesEnum

from src.merchant_request.schemas.create_merchant_request_schema import CreateMerchantRequestSchema
from src.merchant_request.service import MerchantRequestService

merchant_request_service = MerchantRequestService()

create_merchant_request_schema = CreateMerchantRequestSchema()

merchant_request_bp = Blueprint('merchant_request', __name__, url_prefix='/merchant_request')


@merchant_request_bp.route('/', methods=['POST'])
def create_merchant_request():
    try:

        data = create_merchant_request_schema.load(request.form)

        if 'shop_image' not in request.files:
            print(f'create_merchant_request - failed : no shop_image')
            raise CustomException(400, "Please add shop image!", ErrorTypesEnum.BAD_REQUEST_ERROR.value)

        shop_image = request.files['shop_image']

        if shop_image.filename == '':
            print(f'create_merchant_request - failed : no selected shop_image')
            raise CustomException(400, "No selected shop image!", ErrorTypesEnum.BAD_REQUEST_ERROR.value)

        result = merchant_request_service.create_merchant_request(data, shop_image)

        return ApiResponse.success_response(201, 'Merchant request created successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@merchant_request_bp.route('/', methods=['GET'])
@jwt_required()
@role_required([UserRolesEnum.ADMIN.value])
def get_merchant_requests():
    try:

        result = merchant_request_service.get_merchant_requests()

        return ApiResponse.success_response(200, 'Merchant requests fetched successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)
