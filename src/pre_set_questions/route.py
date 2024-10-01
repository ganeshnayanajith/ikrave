from flask import Blueprint
from marshmallow import ValidationError

from libs.helpers import ApiResponse, CustomException, error_response_handler

from src.pre_set_questions.service import PreSetQuestionService

pre_set_question_service = PreSetQuestionService()

pre_set_question_bp = Blueprint('pre_set_question', __name__, url_prefix='/pre_set_question')


@pre_set_question_bp.route('/', methods=['GET'])
def get_pre_set_questions():
    try:

        result = pre_set_question_service.get_pre_set_questions()

        return ApiResponse.success_response(200, 'Pre set questions fetched successfully', result)

    except (ValidationError, CustomException, Exception) as err:
        return error_response_handler(err)
