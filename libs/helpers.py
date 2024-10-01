from flask import jsonify, make_response
from functools import wraps
from flask_jwt_extended import get_jwt_identity
from marshmallow import ValidationError
from bson import ObjectId
import bcrypt
from flask_jwt_extended import create_access_token
from datetime import timedelta
import math

from libs.enums import ErrorTypesEnum
from libs.email_service import EmailService

email_service = EmailService()


class CustomException(Exception):
    def __init__(self, status_code, message, error):
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.error = error


class ApiResponse:
    @staticmethod
    def success_response(status_code, message, data):
        response = {
            "status": True,
            "statusCode": status_code,
            "message": message,
            "data": data,
            "error": None
        }

        response = make_response(jsonify(response))

        # response.headers['Access-Control-Allow-Origin'] = '*'
        # response.headers['Access-Control-Allow-Methods'] = '*'
        # response.headers['Access-Control-Allow-Headers'] = '*'

        return response, status_code

    @staticmethod
    def error_response(err: CustomException = None):
        status_code = getattr(err, 'status_code', 500)
        message = getattr(err, 'message', ErrorTypesEnum.INTERNAL_SERVER_ERROR.value)
        error = getattr(err, 'error', ErrorTypesEnum.INTERNAL_SERVER_ERROR.value)

        response = {
            "status": False,
            "statusCode": status_code,
            "message": message,
            "error": error,
            "data": None,
        }

        response = make_response(jsonify(response))

        # response.headers['Access-Control-Allow-Origin'] = '*'
        # response.headers['Access-Control-Allow-Methods'] = '*'
        # response.headers['Access-Control-Allow-Headers'] = '*'

        return response, status_code


def role_required(roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(*args, **kwargs):
            current_user_role = get_jwt_identity().get('role', str)
            if current_user_role not in roles:
                return ApiResponse.error_response(
                    CustomException(403, 'Insufficient permissions', ErrorTypesEnum.FORBIDDEN_ERROR.value))
            return view_func(*args, **kwargs)

        return wrapper

    return decorator


def error_response_handler(err):
    if hasattr(type(err), '__name__'):
        error = type(err).__name__
    else:
        error = ErrorTypesEnum.INTERNAL_SERVER_ERROR.value

    print('*******************************')
    print(f'{error}: {err}')
    print('*******************************')

    if isinstance(err, ValidationError):
        print('--------------------------------')
        print('ValidationError :', err)
        print('--------------------------------')
        status_code = 400
        message = str(err)
        error = ErrorTypesEnum.BAD_REQUEST_ERROR.value
    elif isinstance(err, CustomException):
        print('--------------------------------')
        print('CustomException :', err)
        print('--------------------------------')
        status_code = getattr(err, 'status_code', 500)
        message = getattr(err, 'message', 'Something went wrong!')
        error = getattr(err, 'error', error)
    else:
        print('--------------------------------')
        print('Unexpected error:', err)
        print('--------------------------------')
        status_code = 500
        message = str(err)
        error = error

    return ApiResponse.error_response(CustomException(status_code, message, error))


def convert_object_ids_to_strings(obj):
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, ObjectId):
                obj[key] = str(value)
            elif isinstance(value, dict):
                obj[key] = convert_object_ids_to_strings(value)
            elif isinstance(value, list):
                obj[key] = [convert_object_ids_to_strings(item) for item in value]
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            obj[i] = convert_object_ids_to_strings(item)
    return obj


def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password


def compare_password(input_password, hashed_password):
    return bcrypt.checkpw(input_password.encode('utf-8'), hashed_password)


def generate_access_token(payload):
    expiry_delta = timedelta(days=21)
    return create_access_token(identity=payload, additional_claims=payload, expires_delta=expiry_delta)


def send_verification_email(receiver_email, verification_code):
    subject = "Welcome to IKRAVE. Use below code to verify your email address."
    body = f"Verification code : {verification_code}"

    email_service.send_email(receiver_email, subject, body)


def haversine(lat1, lon1, lat2, lon2):
    # Radius of the Earth in kilometers
    r = 6371

    # Convert latitude and longitude from degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    diff_lat = lat2_rad - lat1_rad
    diff_lon = lon2_rad - lon1_rad

    # Calculate distance using Haversine formula
    a = math.sin(diff_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(diff_lon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # Distance in kilometers
    distance = r * c

    return distance
