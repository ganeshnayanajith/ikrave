from datetime import datetime, timezone
from bson import ObjectId

from libs.db import connect_to_mongodb
from libs.enums import UserRolesEnum, MerchantRequestStatusEnum
from libs.helpers import CustomException, convert_object_ids_to_strings, compare_password, hash_password, \
    generate_access_token, haversine
from libs.enums import ErrorTypesEnum

from src.merchant_request.service import MerchantRequestService

merchant_request_service = MerchantRequestService()


class MerchantService:
    def __init__(self) -> None:
        self.conn = connect_to_mongodb()
        self.db = self.conn.ikrave
        self.merchants_collection = self.db.merchants

    def add_merchant(self, admin_id: str, request_id: str):
        merchant_request = merchant_request_service.get_merchant_request(request_id)

        if merchant_request is None:
            print(f'add_merchant - merchant request not found for {request_id}')
            raise CustomException(404, 'Merchant request is not found', ErrorTypesEnum.NOT_FOUND_ERROR.value)

        if not merchant_request['status'] == MerchantRequestStatusEnum.PENDING.value:
            print(f'add_merchant - merchant request status is not PENDING for {request_id}')
            raise CustomException(400, 'Merchant request status is not PENDING', ErrorTypesEnum.BAD_REQUEST_ERROR.value)

        merchant_data = {
            'username': merchant_request['username'],
            'password': hash_password('password'),
            'business_name': merchant_request['business_name'],
            'business_registration': merchant_request['business_registration'],
            'food_hygiene_rating': merchant_request['food_hygiene_rating'],
            'business_address': merchant_request['business_address'],
            'phone_number': merchant_request['phone_number'],
            'opening_hours': merchant_request['opening_hours'],
            'closing_hours': merchant_request['closing_hours'],
            'geo_location': merchant_request['geo_location'],
            'shop_image_url': merchant_request['shop_image_url'],
            'latitude': merchant_request['latitude'],
            'longitude': merchant_request['longitude'],
            'is_available': True,
            'created_by': ObjectId(admin_id)
        }

        merchant = self.create_merchant(merchant_data)

        updated_request = merchant_request_service.update_merchant_request_status(request_id,
                                                                                  MerchantRequestStatusEnum.ACCEPTED.value)

        print(f'add_merchant - success')

        return {
            "merchant": merchant,
            "merchant_request": updated_request
        }

    def create_merchant(self, merchant_data):

        current_timestamp = datetime.now(tz=timezone.utc)

        merchant_data['role'] = UserRolesEnum.MERCHANT.value
        merchant_data['created_at'] = current_timestamp
        merchant_data['updated_at'] = current_timestamp

        merchant_inserted_result = self.merchants_collection.insert_one(merchant_data)
        print(f'create_merchant - success : {merchant_inserted_result}')

        merchant = self.get_merchant(merchant_inserted_result.inserted_id)
        print(f'create_merchant - find_one : {merchant}')
        merchant = convert_object_ids_to_strings(merchant)

        return merchant

    def get_merchants(self):
        cursor = self.merchants_collection.find()
        documents = []
        for document in cursor:
            document = convert_object_ids_to_strings(document)
            del document["password"]
            documents.append(document)
        print(f'get_merchants - success : {documents}')
        return documents

    def login_merchant(self, username: str, password: str):
        merchant = self.merchants_collection.find_one({"username": username, "role": UserRolesEnum.MERCHANT.value})

        if merchant is None:
            print(f'login_merchant - no merchant found for {username} and {password}')
            raise CustomException(401, 'Invalid username', ErrorTypesEnum.UNAUTHORIZED_ERROR.value)

        if compare_password(password, merchant['password']):
            merchant = convert_object_ids_to_strings(merchant)
            del merchant["password"]
            access_token = generate_access_token(merchant)

            print(f'login_merchant - success : {merchant} for {username} and {password}')

            return {
                "access_token": access_token,
                "merchant": merchant
            }
        else:
            raise CustomException(401, 'Invalid password', ErrorTypesEnum.UNAUTHORIZED_ERROR.value)

    def get_merchant(self, merchant_id: str):
        merchant = self.merchants_collection.find_one(
            {"_id": ObjectId(merchant_id), "role": UserRolesEnum.MERCHANT.value})
        if merchant is None:
            print(f'get_merchant - failed - no merchant found for {merchant_id}')
            raise CustomException(404, 'Merchant not found', ErrorTypesEnum.NOT_FOUND_ERROR.value)

        del merchant["password"]
        print(f'get_merchant - success : {merchant} for {merchant_id}')
        merchant = convert_object_ids_to_strings(merchant)
        return merchant

    def update_merchant(self, merchant_id, update_data):

        update_query = {"$set": {key: value for key, value in update_data.items()}}

        update_query["$set"]["updated_at"] = datetime.now(timezone.utc)

        print(f'update_merchant - starting : {merchant_id} {update_query}')

        updated_result = self.merchants_collection.update_one({"_id": ObjectId(merchant_id)}, update_query)

        print(f'update_merchant - success : {updated_result}')

        merchant = self.get_merchant(merchant_id)
        print(f'update_merchant - find_one : {merchant}')
        return merchant

    def get_nearby_merchants(self, latitude, longitude):

        # Convert miles to kilometers
        max_distance_km = 2 * 1.60934

        nearby_merchants = []

        merchants = self.get_merchants()

        for merchant in merchants:
            merchant_lat = merchant['latitude']
            merchant_lon = merchant['longitude']
            distance = haversine(latitude, longitude, merchant_lat, merchant_lon)
            if distance <= max_distance_km:
                nearby_merchants.append(merchant)

        print(f'get_nearby_merchants - success : {nearby_merchants}')

        return nearby_merchants
