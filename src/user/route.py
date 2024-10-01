from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from libs.helpers import ApiResponse, CustomException, role_required, error_response_handler
from libs.enums import UserRolesEnum
from src.user.schemas.verify_email_schema import VerifyEmailSchema

from src.user.service import UserService
from src.user.schemas.email_register_schema import EmailRegisterSchema
from src.user.schemas.login_schema import LoginSchema
from src.user.schemas.update_profile_schema import UpdateProfileSchema

user_service = UserService()

email_register_schema = EmailRegisterSchema()
login_schema = LoginSchema()
update_profile_schema = UpdateProfileSchema()
verify_email_schema = VerifyEmailSchema()

user_bp = Blueprint('user', __name__, url_prefix='/user')


@user_bp.route('/email_register', methods=['POST'])
def email_register():
    try:

        data = email_register_schema.load(request.get_json())
        data['role'] = UserRolesEnum.USER.value
        result = user_service.create_new_user(data)

        return ApiResponse.success_response(201, "User created successfully", result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@user_bp.route('/login', methods=['POST'])
def login():
    try:

        data = login_schema.load(request.get_json())

        result = user_service.login_user(data.get('username'), data.get('password'), data.get('device_token'))

        return ApiResponse.success_response(200, 'Login successful', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@user_bp.route('/profile', methods=['GET'])
@jwt_required()
@role_required([UserRolesEnum.USER.value])
def get_user_profile():
    try:

        user = get_jwt_identity()

        result = user_service.get_user_by_id(user["_id"])

        return ApiResponse.success_response(200, 'User profile fetched successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
@role_required([UserRolesEnum.USER.value])
def update_profile():
    try:

        user = get_jwt_identity()

        data = update_profile_schema.load(request.get_json())

        result = user_service.update_profile(user["_id"], data)

        return ApiResponse.success_response(200, 'User profile updated successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@user_bp.route('/verify_email', methods=['POST'])
@jwt_required()
@role_required([UserRolesEnum.USER.value])
def verify_email():
    try:

        user = get_jwt_identity()

        data = verify_email_schema.load(request.get_json())

        result = user_service.verify_email(user["_id"], data.get('verification_code'))

        return ApiResponse.success_response(200, 'Email verified successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)


@user_bp.route('/resend_verify_email', methods=['GET'])
@jwt_required()
@role_required([UserRolesEnum.USER.value])
def resend_verify_email():
    try:

        user = get_jwt_identity()

        result = user_service.resend_verify_email(user["_id"])

        return ApiResponse.success_response(200, 'Verification email has been sent successfully!', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)
