from flask import Blueprint, request
from libs.helpers import ApiResponse, CustomException, error_response_handler
from marshmallow import ValidationError
from src.admin.service import AdminService
from src.user.schemas.login_schema import LoginSchema

admin_service = AdminService()

login_schema = LoginSchema()

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/login', methods=['POST'])
def login():
    try:

        data = login_schema.load(request.get_json())

        result = admin_service.login_admin(data.get('username'), data.get('password'))

        return ApiResponse.success_response(200, 'Admin Login successful', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)
