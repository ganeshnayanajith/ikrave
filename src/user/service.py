from datetime import datetime, timezone
from bson import ObjectId
import random

from libs.db import connect_to_mongodb
from libs.enums import UserRolesEnum, ErrorTypesEnum
from libs.helpers import convert_object_ids_to_strings, hash_password, compare_password, CustomException, \
    generate_access_token, send_verification_email

from src.cart.service import CartService

cart_service = CartService()


class UserService:
    def __init__(self) -> None:
        self.conn = connect_to_mongodb()
        self.db = self.conn.ikrave
        self.users_collection = self.db.users

    def create_new_user(self, user_data):

        user_data["password"] = hash_password(user_data["password"])

        current_timestamp = datetime.now(tz=timezone.utc)

        user_data['is_email_verified'] = False
        user_data['created_at'] = current_timestamp
        user_data['updated_at'] = current_timestamp

        user_inserted_result = self.users_collection.insert_one(user_data)
        print(f'create_new_user - success : {user_inserted_result}')

        user = self.users_collection.find_one({'_id': user_inserted_result.inserted_id})
        print(f'create_new_user - find_one : {user}')
        user = convert_object_ids_to_strings(user)
        del user['password']

        cart = cart_service.create_cart({"user_id": user_inserted_result.inserted_id, "items": []})

        access_token = generate_access_token(user)

        # send verification email
        verification_code = random.randint(100000, 999999)
        send_verification_email(user_data['email'], verification_code)

        self.update_profile(user['_id'], {'verification_code': verification_code})

        return {
            "user": user,
            "cart": cart,
            "access_token": access_token
        }

    def login_user(self, username: str, password: str, device_token: str):
        user = self.users_collection.find_one({"username": username, "role": UserRolesEnum.USER.value})

        if user is None:
            raise CustomException(401, 'Invalid username', ErrorTypesEnum.UNAUTHORIZED_ERROR.value)

        if compare_password(password, user['password']):

            user = convert_object_ids_to_strings(user)

            self.update_profile(user['_id'], {'device_token': device_token})

            del user["password"]
            access_token = generate_access_token(user)
            return {
                "access_token": access_token,
                "user": user
            }
        else:
            raise CustomException(401, 'Invalid password', ErrorTypesEnum.UNAUTHORIZED_ERROR.value)

    def get_user_by_id(self, user_id: str):
        user = self.users_collection.find_one({"_id": ObjectId(user_id), "role": UserRolesEnum.USER.value})
        if user is None:
            print(f'get_user_by_id - no user found for {user_id}')
            raise CustomException(404, 'User is not found!', ErrorTypesEnum.NOT_FOUND_ERROR.value)

        print(f'get_user_by_id - success : {user} for {user_id}')

        del user["password"]

        if 'verification_code' in user:
            del user['verification_code']

        user = convert_object_ids_to_strings(user)
        return user

    def update_profile(self, user_id, update_data):

        update_query = {"$set": {key: value for key, value in update_data.items()}}
        update_query["$set"]["updated_at"] = datetime.now(timezone.utc)

        print(f'update_profile - starting : {user_id} {update_query}')

        updated_result = self.users_collection.update_one({"_id": ObjectId(user_id)}, update_query)

        print(f'update_profile - success : {updated_result}')

        user = self.get_user_by_id(user_id)
        return user

    def get_pre_set_questions(self):
        cursor = self.users_collection.find()
        documents = []
        for document in cursor:
            document['_id'] = str(document['_id'])
            documents.append(document)
        print(f'get_pre_set_questions - success : {documents}')
        return documents

    def verify_email(self, user_id: str, verification_code: int):
        user = self.users_collection.find_one({"_id": ObjectId(user_id), "role": UserRolesEnum.USER.value})
        if user is None:
            print(f'verify_email - no user found for {user_id}')
            raise CustomException(404, 'User is not found!', ErrorTypesEnum.NOT_FOUND_ERROR.value)

        if user['verification_code'] != verification_code:
            print(f'verify_email - failed')
            raise CustomException(400, 'Invalid verification code', ErrorTypesEnum.BAD_REQUEST_ERROR.value)

        self.update_profile(user_id, {'is_email_verified': True})

        user = self.get_user_by_id(user_id)

        return user

    def resend_verify_email(self, user_id: str):

        user = self.get_user_by_id(user_id)

        # send verification email
        verification_code = random.randint(100000, 999999)
        send_verification_email(user['email'], verification_code)

        self.update_profile(user['_id'], {'verification_code': verification_code})

        return {'message': 'Email has been sent successfully!'}

    def get_user_favorite_foods(self, user_id: str):

        user = self.get_user_by_id(user_id)

        answer = None
        for preference in user.get('preferences', []):
            if preference.get('question') == 'What are your most favourite beverages and dishes?':
                answer = preference.get('answer')
                break

        if answer is None:
            print(f'get_user_favorite_foods - failed - no favorite foods')
            raise CustomException(404, 'No food preferences found. Please answer the questions.',
                                  ErrorTypesEnum.NOT_FOUND_ERROR.value)

        print(f'get_user_favorite_foods - success : {answer}')

        return answer

    def get_user_favorite_cuisine_types(self, user_id: str):

        user = self.get_user_by_id(user_id)

        answer = None
        for preference in user.get('preferences', []):
            if preference.get('question') == 'What types of cuisine do you most prefer?':
                answer = preference.get('answer')
                break

        if answer is None:
            print(f'get_user_favorite_cuisine_types - failed - no favorite cuisine types')
            raise CustomException(404, 'No cuisine type preferences found. Please answer the questions.',
                                  ErrorTypesEnum.NOT_FOUND_ERROR.value)

        print(f'get_user_favorite_cuisine_types - success : {answer}')

        return answer
