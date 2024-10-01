from flask import Blueprint, request
from marshmallow import ValidationError
from flask_jwt_extended import jwt_required, get_jwt_identity

from libs.helpers import ApiResponse, CustomException, role_required, error_response_handler
from libs.enums import UserRolesEnum, ErrorTypesEnum
from src.user.schemas.login_schema import LoginSchema
from src.driver.schemas.add_driver_schema import AddDriverSchema
from src.driver.schemas.assign_driver_schema import AssignDriverSchema
from src.driver.schemas.driver_profile_update_schema import DriverProfileUpdateSchema
from src.driver.service import DriverService

driver_service = DriverService()

assign_driver_schema = AssignDriverSchema()
driver_profile_update_schema = DriverProfileUpdateSchema()
login_schema = LoginSchema()
add_driver_schema = AddDriverSchema()

driver_bp = Blueprint('driver', __name__, url_prefix='/driver')


@driver_bp.route('/', methods=['POST'])
@jwt_required()
@role_required([UserRolesEnum.ADMIN.value])
def add_driver():
    try:
        admin = get_jwt_identity()

        data = add_driver_schema.load(request.form)

        if 'photo' not in request.files:
            print(f'add_driver - failed : no photo')
            raise CustomException(400, "Please add photo!", ErrorTypesEnum.BAD_REQUEST_ERROR.value)

        photo = request.files['photo']

        if photo.filename == '':
            print(f'add_driver - failed : no selected photo')
            raise CustomException(400, "No selected photo!", ErrorTypesEnum.BAD_REQUEST_ERROR.value)

        result = driver_service.create_driver(admin["_id"], data, photo)

        return ApiResponse.success_response(201, 'Driver added successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@driver_bp.route('/login', methods=['POST'])
def login():
    try:

        data = login_schema.load(request.get_json())

        result = driver_service.login_driver(data.get('username'), data.get('password'))

        return ApiResponse.success_response(200, 'Login successful', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@driver_bp.route('/profile', methods=['PUT'])
@jwt_required()
@role_required([UserRolesEnum.DRIVER.value])
def update_driver_profile():
    try:

        driver = get_jwt_identity()

        data = driver_profile_update_schema.load(request.get_json())

        result = driver_service.update_driver(driver["_id"], data)

        return ApiResponse.success_response(200, 'Driver profile updated successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)
