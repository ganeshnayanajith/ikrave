from bson import ObjectId
from datetime import datetime, timezone
from typing import Optional

from libs.db import connect_to_mongodb
from libs.fcm_service import FCMService
from libs.helpers import CustomException, convert_object_ids_to_strings
from libs.enums import ErrorTypesEnum, OrderStatusEnum

from src.food.service import FoodService
from src.merchant.service import MerchantService
from src.user.service import UserService

# fcm_service = FCMService()
user_service = UserService()
merchant_service = MerchantService()
food_service = FoodService()


class MerchantOrderService:
    def __init__(self) -> None:
        self.conn = connect_to_mongodb()
        self.db = self.conn.ikrave
        self.merchant_orders_collection = self.db.merchant_orders

    def get_merchant_orders_by_merchant_id(self, merchant_id: str, status: Optional[OrderStatusEnum] = None):

        query = {"merchant_id": ObjectId(merchant_id)}

        if status is not None:
            query["status"] = status

        cursor = self.merchant_orders_collection.find(query)
        documents = []

        for document in cursor:
            document = convert_object_ids_to_strings(document)
            merchant_data = merchant_service.get_merchant(document['merchant_id'])
            document['merchant_data'] = merchant_data

            for item in document['items']:
                food_data = food_service.get_food_item_by_food_id(item['food_id'])
                item['food_data'] = food_data

            documents.append(document)

        print(f'get_merchant_orders_by_merchant_id - success : {documents}')
        return documents

    def get_merchant_order_by_merchant_id_and_order_id(self, merchant_id: str, merchant_order_id: str):
        merchant_order = self.merchant_orders_collection.find_one({
            "merchant_id": ObjectId(merchant_id),
            "_id": ObjectId(merchant_order_id)
        })

        if merchant_order is None:
            print(
                f'get_merchant_order_by_merchant_id_and_order_id - merchant order not found for merchant_id : {merchant_id}, merchant_order_id : {merchant_order_id}')
            raise CustomException(404, "Merchant order not found!", ErrorTypesEnum.NOT_FOUND_ERROR.value)

        merchant_order = convert_object_ids_to_strings(merchant_order)

        merchant_data = merchant_service.get_merchant(merchant_order['merchant_id'])
        merchant_order['merchant_data'] = merchant_data

        for item in merchant_order['items']:
            food_data = food_service.get_food_item_by_food_id(item['food_id'])
            item['food_data'] = food_data

        print(f'get_merchant_order_by_merchant_id_and_order_id - success : {merchant_order}')
        return merchant_order

    def get_merchant_orders_by_user_id_and_order_id(self, user_id: str, order_id: str):
        cursor = self.merchant_orders_collection.find({
            "order_id": ObjectId(order_id),
            "user_id": ObjectId(user_id)
        })

        documents = []

        for document in cursor:
            document = convert_object_ids_to_strings(document)
            documents.append(document)

        print(f'get_merchant_orders_by_user_id_and_order_id - success : {documents}')
        return documents

    def add_multiple_merchant_orders(self, merchant_orders):
        merchant_orders_inserted_result = self.merchant_orders_collection.insert_many(merchant_orders)

        print(f'add_multiple_merchant_orders - success : {merchant_orders_inserted_result}')

    def update_merchant_orders_by_order_id(self, order_id: str, update_data):
        update_query = {
            "$set": {
                "updated_at": datetime.now(timezone.utc)
            }
        }

        for key, value in update_data.items():
            update_query["$set"][key] = value

        updated_result = self.merchant_orders_collection.update_many({"order_id": ObjectId(order_id)}, update_query)

        print(f'update_merchant_orders_by_order_id - success - {updated_result}')

    def update_merchant_order(self, merchant_id: str, order_id: str, merchant_order_id: str, merchant_order_data: dict):

        merchant_order = self.merchant_orders_collection.find_one({
            "_id": ObjectId(merchant_order_id),
            "order_id": ObjectId(order_id),
            "merchant_id": ObjectId(merchant_id)
        })

        if merchant_order is None:
            print(
                f'update_merchant_order - merchant order not found for merchant_id : {merchant_id}, order_id : {order_id}, merchant_order_id : {merchant_order_id}')
            raise CustomException(404, "Merchant order not found!", ErrorTypesEnum.NOT_FOUND_ERROR.value)

        update_query = {
            "$set": {
                "updated_at": datetime.now(timezone.utc)
            }
        }

        for key, value in merchant_order_data.items():
            update_query["$set"][key] = value

        updated_result = self.merchant_orders_collection.update_one({"_id": ObjectId(merchant_order_id)}, update_query)

        print(f'update_merchant_order - success - {updated_result}')

        if "status" in merchant_order_data:
            notification_title = f"Merchant order status updated : {merchant_order_data['status']}"
            notification_body = f"Your merchant order status has been updated to {merchant_order_data['status']} status."

            user = user_service.get_user_by_id(merchant_order["user_id"])

            # fcm_service.send_notification(notification_title, notification_body, user["token"])

            print(
                f'update_merchant_order - notification success - title : {notification_title} - body : {notification_body}')

        merchant_order = self.get_merchant_order_by_merchant_id_and_order_id(merchant_id, merchant_order_id)
        print(f'update_merchant_order - find_one - {merchant_order}')
        return merchant_order
