from datetime import datetime, timezone
from bson import ObjectId

from libs.db import connect_to_mongodb
from libs.enums import MerchantRequestStatusEnum
from libs.helpers import convert_object_ids_to_strings
from libs.firebase_storage_service import FirebaseStorageService

firebase_storage_service = FirebaseStorageService()


class MerchantRequestService:
    def __init__(self) -> None:
        self.conn = connect_to_mongodb()
        self.db = self.conn.ikrave
        self.merchant_requests_collection = self.db.merchant_requests

    def create_merchant_request(self, request_data, file):
        current_timestamp = datetime.now(tz=timezone.utc)

        request_data['status'] = MerchantRequestStatusEnum.PENDING.value
        request_data['created_at'] = current_timestamp
        request_data['updated_at'] = current_timestamp

        request_inserted_result = self.merchant_requests_collection.insert_one(request_data)
        print(f'create_merchant_request - success : {request_inserted_result}')

        folder_path = f'merchant/{request_data["username"]}'

        url = firebase_storage_service.upload_file(file, folder_path)
        print(f'create_merchant_request - file upload success - {url}')

        request = self.update_merchant_request(str(request_inserted_result.inserted_id), {'shop_image_url': url})
        print(f'create_merchant_request - update_merchant_request : {request}')

        return request

    def get_merchant_request(self, request_id: str):
        request = self.merchant_requests_collection.find_one({"_id": ObjectId(request_id)})
        print(f'get_merchant_request - success : {request}')
        request = convert_object_ids_to_strings(request)
        return request

    def get_merchant_requests(self):
        cursor = self.merchant_requests_collection.find()
        documents = []
        for document in cursor:
            document['_id'] = str(document['_id'])
            documents.append(document)
        print(f'get_merchant_requests - success : {documents}')
        return documents

    def update_merchant_request_status(self, request_id: str, status):
        update_query = {
            "$set": {
                "status": status,
                "updated_at": datetime.now(timezone.utc)
            }
        }
        print(f'update_merchant_request_status - starting : {request_id} {update_query}')
        updated_result = self.merchant_requests_collection.update_one({"_id": ObjectId(request_id)}, update_query)
        print(f'update_merchant_request_status - success : {updated_result}')

        request = self.get_merchant_request(request_id)
        print(f'update_merchant_request_status - find_one : {request}')

        return request

    def update_merchant_request(self, request_id: str, update_data):
        update_query = {
            "$set": {
                "updated_at": datetime.now(timezone.utc)
            }
        }

        for key, value in update_data.items():
            update_query["$set"][key] = value

        print(f'update_merchant_request - starting : {request_id} {update_query}')
        updated_result = self.merchant_requests_collection.update_one({"_id": ObjectId(request_id)}, update_query)
        print(f'update_merchant_request - success : {updated_result}')

        request = self.get_merchant_request(request_id)
        print(f'update_merchant_request - find_one : {request}')

        return request
