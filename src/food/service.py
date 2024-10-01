from datetime import datetime, timezone
from bson import ObjectId

from libs.db import connect_to_mongodb
from libs.helpers import convert_object_ids_to_strings, CustomException, ErrorTypesEnum
from libs.firebase_storage_service import FirebaseStorageService

from src.merchant.service import MerchantService

firebase_storage_service = FirebaseStorageService()

merchant_service = MerchantService()


class FoodService:
    def __init__(self) -> None:
        self.conn = connect_to_mongodb()
        self.db = self.conn.ikrave
        self.foods_collection = self.db.foods

    def add_food_item(self, merchant_id: str, item_data, file):

        current_timestamp = datetime.now(tz=timezone.utc)

        item_data['allergens'] = item_data['allergens'].split(",")
        item_data['rating'] = 0
        item_data['merchant_id'] = ObjectId(merchant_id)
        item_data['created_at'] = current_timestamp
        item_data['updated_at'] = current_timestamp

        inserted_result = self.foods_collection.insert_one(item_data)
        print(f'add_food_item - success : {inserted_result}')

        merchant = merchant_service.get_merchant(merchant_id)

        folder_path = f'merchant/{merchant["username"]}'

        url = firebase_storage_service.upload_file(file, folder_path)
        print(f'add_food_item - file upload success - {url}')

        food_item = self.update_food_item(str(inserted_result.inserted_id), {'food_image_url': url})
        print(f'add_food_item - update_food_item : {food_item}')

        return food_item

    def get_food_items(self, merchant_id: str):
        cursor = self.foods_collection.find({'merchant_id': ObjectId(merchant_id)})
        documents = []
        for document in cursor:
            document['_id'] = str(document['_id'])
            document['merchant_id'] = str(document['merchant_id'])
            documents.append(document)
        print(f'get_food_items - success : {documents}')
        return documents

    def get_food_item_by_food_id_and_merchant_id(self, merchant_id: str, food_item_id: str):
        food_item = self.foods_collection.find_one({
            'merchant_id': ObjectId(merchant_id),
            '_id': ObjectId(food_item_id)
        })
        print(f'get_food_item_by_food_id_and_merchant_id - success : {food_item}')
        food_item = convert_object_ids_to_strings(food_item)
        return food_item

    def get_food_item_by_food_id(self, food_item_id: str):
        food_item = self.foods_collection.find_one({
            '_id': ObjectId(food_item_id)
        })

        if food_item is None:
            print(f'get_food_item_by_food_id - no food item found for : {food_item_id}')
            raise CustomException(404, "Food item not found", ErrorTypesEnum.NOT_FOUND_ERROR.value)

        print(f'get_food_item_by_food_id - success : {food_item}')
        food_item = convert_object_ids_to_strings(food_item)
        return food_item

    def update_food_item(self, food_id: str, update_data: dict):
        filter = {"_id": ObjectId(food_id)}

        update_query = {
            "$set": {
                "updated_at": datetime.now(timezone.utc)
            }
        }

        for key, value in update_data.items():
            update_query["$set"][key] = value

        updated_result = self.foods_collection.update_one(filter, update_query)
        print(f'update_food_item - success : {updated_result}')

        food_item = self.get_food_item_by_food_id(food_id)
        print(f'update_food_item - find_one : {food_item}')
        return food_item

    def delete_food_item(self, food_id: str):
        filter = {"_id": ObjectId(food_id)}

        deletion_result = self.foods_collection.delete_one(filter)

        print(f'delete_food_item - success : {deletion_result}')

    def get_all_food_items(self):
        cursor = self.foods_collection.find()

        documents = []
        for document in cursor:
            document['_id'] = str(document['_id'])
            document['merchant_id'] = str(document['merchant_id'])
            documents.append(document)
        print(f'get_all_food_items - success')
        return documents
