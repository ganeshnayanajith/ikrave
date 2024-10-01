import os
import json

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from pathlib import Path
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS

from libs.helpers import ApiResponse, CustomException
from libs.enums import ErrorTypesEnum

from src.admin.route import admin_bp
from src.cart.route import cart_bp
from src.driver.route import driver_bp
from src.food.route import food_bp
from src.food_recommendation_engine.route import food_recommendation_engine_bp
from src.merchant.route import merchant_bp
from src.merchant_order.route import merchant_order_bp
from src.merchant_request.route import merchant_request_bp
from src.order.route import order_bp
from src.pre_set_questions.route import pre_set_question_bp
from src.user.route import user_bp
from src.schedulers.weekly_charge_from_merchants_scheduler_service import WeeklyChargeFromMerchantsSchedulerService

dotenv_path = Path('./.env')
load_dotenv(dotenv_path=dotenv_path)

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')

app = Flask(__name__)

# Set up Flask-JWT-Extended
app.config['JWT_SECRET_KEY'] = JWT_SECRET_KEY
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config['JWT_HEADER_NAME'] = 'X-Authorization'
app.config['JWT_HEADER_TYPE'] = 'Bearer'
jwt = JWTManager(app)

# Include blueprints
app.register_blueprint(admin_bp)
app.register_blueprint(cart_bp)
app.register_blueprint(driver_bp)
app.register_blueprint(food_bp)
app.register_blueprint(food_recommendation_engine_bp)
app.register_blueprint(merchant_bp)
app.register_blueprint(merchant_order_bp)
app.register_blueprint(merchant_request_bp)
app.register_blueprint(order_bp)
app.register_blueprint(pre_set_question_bp)
app.register_blueprint(user_bp)


def unauthorized_response(callback):
    return ApiResponse.error_response(
        CustomException(401, 'Missing Authorization Header', ErrorTypesEnum.UNAUTHORIZED_ERROR.value))


def expired_token_response(jwt_header, jwt_data):
    return ApiResponse.error_response(CustomException(401, 'Token has expired', ErrorTypesEnum.UNAUTHORIZED_ERROR.value))


def invalid_token_response(error_string):
    return ApiResponse.error_response(CustomException(401, error_string, ErrorTypesEnum.UNAUTHORIZED_ERROR.value))


# Error handlers
jwt.unauthorized_loader(unauthorized_response)
jwt.expired_token_loader(expired_token_response)
jwt.invalid_token_loader(invalid_token_response)

SWAGGER_URL = '/docs'
API_URL = '/swagger.json'

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "IKRAVE - Food Delivery Service"
    }
)

app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


@app.route('/swagger.json')
def swagger():
    with open('swagger.json', 'r') as f:
        return jsonify(json.load(f))


# CORS(app)

# Define allowed origins
allowed_origins = '*'

# Enable CORS for all routes and specify allowed origins
CORS(app, resources={r"/*": {"origins": allowed_origins}})

# weekly_charge_from_merchants_scheduler_service = WeeklyChargeFromMerchantsSchedulerService(app)

if __name__ == '__main__':
    app.run()
