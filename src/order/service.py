from bson import ObjectId
from datetime import datetime, timezone
from typing import List

from libs.db import connect_to_mongodb
from libs.helpers import CustomException, convert_object_ids_to_strings
from libs.enums import ErrorTypesEnum, OrderStatusEnum, DriverStatusEnum, UserRolesEnum

from src.cart.service import CartService
from src.driver.service import DriverService
from src.food.service import FoodService
from src.merchant_order.service import MerchantOrderService
from src.user.service import UserService
from src.merchant.service import MerchantService

cart_service = CartService()
merchant_order_service = MerchantOrderService()
driver_service = DriverService()
user_service = UserService()
merchant_service = MerchantService()
food_service = FoodService()


class OrderService:
    def __init__(self) -> None:
        self.conn = connect_to_mongodb()
        self.db = self.conn.ikrave
        self.orders_collection = self.db.orders

    def create_order(self, user_id: str, data: dict):
        cart_items = cart_service.get_cart_items(user_id)

        if len(cart_items) == 0:
            print(f'create_order - minimum merchant count should be 1')
            raise CustomException(400, "Minimum merchant count should be 1", ErrorTypesEnum.BAD_REQUEST_ERROR.value)

        current_timestamp = datetime.now(tz=timezone.utc)

        items_by_merchant = []

        order_total_price = 0

        for cart_item in cart_items:
            cart_item_id = cart_item["_id"]
            merchant_id = cart_item["merchant_id"]
            food_id = cart_item["food_id"]
            quantity = cart_item["quantity"]
            item_unit_price = cart_item["item_unit_price"]
            item_total_price = cart_item["item_total_price"]

            found_object = next((obj for obj in items_by_merchant if str(obj.get("merchant_id")) == merchant_id), None)

            if found_object is not None:
                found_object["items"].append({
                    "_id": ObjectId(cart_item_id),
                    "food_id": ObjectId(food_id),
                    "quantity": quantity,
                    "item_unit_price": item_unit_price,
                    "item_total_price": item_total_price
                })
                found_object["merchant_order_total_price"] += item_total_price
                order_total_price += item_total_price
            else:
                items_by_merchant.append({
                    "merchant_id": ObjectId(merchant_id),
                    "items": [{
                        "_id": ObjectId(cart_item_id),
                        "food_id": ObjectId(food_id),
                        "quantity": quantity,
                        "item_unit_price": item_unit_price,
                        "item_total_price": item_total_price
                    }],
                    "merchant_order_total_price": item_total_price,
                    "created_at": current_timestamp,
                    "updated_at": current_timestamp
                })
                order_total_price += item_total_price

        merchant_count = len(items_by_merchant)

        if merchant_count > 5:
            print(f'create_order - maximum merchant count should be 5')
            raise CustomException(400, "Maximum merchant count should be 5", ErrorTypesEnum.BAD_REQUEST_ERROR.value)

        extra_delivery_charge = 0

        if merchant_count > 1:
            extra_delivery_charge = (merchant_count - 1) * 0.5

        driver = driver_service.get_available_driver_and_update()

        order_data = {
            'user_id': ObjectId(user_id),
            'items_by_merchant': items_by_merchant,
            'status': OrderStatusEnum.PENDING.value,
            'delivery_address': data['delivery_address'],
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'payment_method': data['payment_method'],
            'order_total_price': order_total_price,
            'service_charge': 1,
            'standard_delivery_charge': 1,
            'extra_delivery_charge': extra_delivery_charge,
            'total_delivery_charge': 1 + extra_delivery_charge,
            'final_order_price': order_total_price + 2 + extra_delivery_charge,
            'driver_id': ObjectId(driver['_id']),
            'created_at': current_timestamp,
            'updated_at': current_timestamp
        }

        order_inserted_result = self.orders_collection.insert_one(order_data)

        print(f'create_order - order - success : {order_inserted_result}')

        order_id_str = str(order_inserted_result.inserted_id)

        order = self.get_order_by_order_id(order_id_str)

        merchant_orders = []

        for merchant_obj in items_by_merchant:
            merchant_order = {
                'user_id': ObjectId(user_id),
                'order_id': order_inserted_result.inserted_id,
                'delivery_address': data['delivery_address'],
                'latitude': data['latitude'],
                'longitude': data['longitude'],
                'driver_id': ObjectId(driver['_id']),
                "status": OrderStatusEnum.PENDING.value,
            }

            for key, value in merchant_obj.items():
                merchant_order[key] = value
            merchant_orders.append(merchant_order)

        merchant_order_service.add_multiple_merchant_orders(merchant_orders)

        merchant_orders = merchant_order_service.get_merchant_orders_by_user_id_and_order_id(user_id, order_id_str)

        cart = cart_service.clear_cart(user_id)

        # adding merchant order id to the items_by_merchant in order

        for merchant_order in merchant_orders:
            order_update_query = {
                "_id": ObjectId(order_id_str),
                "items_by_merchant.merchant_id": ObjectId(merchant_order['merchant_id'])
            }

            order_update_data = {"items_by_merchant.$.merchant_order_id": ObjectId(merchant_order['_id'])}

            self.update_order_by_query(order_update_query, order_update_data)

        order = self.get_order_by_order_id(order_id_str)

        # send a notification to the user

        user_notification_title = f"Order placed successfully."
        user_notification_body = f"Your order has been placed successfully."

        user = user_service.get_user_by_id(user_id)

        # fcm_service.send_notification(user_notification_title, user_notification_body, user["token"])

        # send a notification to the driver

        driver_notification_title = f"New order received."
        driver_notification_body = f"Your have been assigned to a new order."

        # fcm_service.send_notification(driver_notification_title, driver_notification_body, driver["token"])

        # send a notification to each merchant

        merchant_notification_title = f"New order received."
        merchant_notification_body = f"Your have received a new order."

        # for merchant_order in merchant_orders:
        #     merchant = merchant_service.get_merchant(merchant_order["merchant_id"])
        #     fcm_service.send_notification(driver_notification_title, driver_notification_body, merchant["token"])

        return {
            "order": order,
            "merchant_orders": merchant_orders,
            "cart": cart,
            "driver": driver
        }

    def get_order_by_user_id_and_order_id(self, user_id: str, order_id: str):
        order = self.orders_collection.find_one({"_id": ObjectId(order_id), "user_id": ObjectId(user_id)})
        if order is None:
            print(f'get_order_by_user_id_and_order_id - no order found for : {order_id}')
            raise CustomException(404, "Order not found", ErrorTypesEnum.NOT_FOUND_ERROR.value)

        order = convert_object_ids_to_strings(order)

        for items_by_merchant in order['items_by_merchant']:
            merchant = merchant_service.get_merchant(items_by_merchant['merchant_id'])
            items_by_merchant['merchant_data'] = merchant

            merchant_order = merchant_order_service.get_merchant_order_by_merchant_id_and_order_id(
                items_by_merchant['merchant_id'], items_by_merchant['merchant_order_id'])
            items_by_merchant['merchant_order_data'] = merchant_order

            for item in items_by_merchant['items']:
                food_item = food_service.get_food_item_by_food_id(item['food_id'])
                item['food_data'] = food_item

        print(f'get_order_by_user_id_and_order_id - success : {order}')
        return order

    def get_orders_by_user_id_and_type(self, user_id: str, user_type: UserRolesEnum, statuses: List[OrderStatusEnum]):

        if user_type == UserRolesEnum.DRIVER.value:
            query = {"driver_id": ObjectId(user_id)}
        elif user_type == UserRolesEnum.USER.value:
            query = {"user_id": ObjectId(user_id)}
        else:
            raise CustomException(403, "Invalid user role", ErrorTypesEnum.FORBIDDEN_ERROR.value)

        valid_statuses = {item.value for item in OrderStatusEnum}

        for status in statuses:
            if status not in valid_statuses:
                raise CustomException(400, f"Invalid status : {status}", ErrorTypesEnum.BAD_REQUEST_ERROR.value)

        if statuses:
            query["status"] = {'$in': [status for status in statuses]}

        cursor = self.orders_collection.find(query)

        orders = []

        for order in cursor:
            order = convert_object_ids_to_strings(order)

            for items_by_merchant in order['items_by_merchant']:
                merchant = merchant_service.get_merchant(items_by_merchant['merchant_id'])
                items_by_merchant['merchant_data'] = merchant

                merchant_order = merchant_order_service.get_merchant_order_by_merchant_id_and_order_id(
                    items_by_merchant['merchant_id'], items_by_merchant['merchant_order_id'])
                items_by_merchant['merchant_order_data'] = merchant_order

                for item in items_by_merchant['items']:
                    food_item = food_service.get_food_item_by_food_id(item['food_id'])
                    item['food_data'] = food_item

            orders.append(order)

        print(f'get_orders_by_user_id_and_type - success : {orders}')
        return orders

    def update_order(self, order_id: str, order_data):
        update_query = {
            "$set": {
                "updated_at": datetime.now(timezone.utc)
            }
        }

        for key, value in order_data.items():
            update_query["$set"][key] = value

        updated_result = self.orders_collection.update_one({"_id": ObjectId(order_id)}, update_query)

        print(f'update_order - success - {updated_result}')

    def update_order_by_query(self, query: dict, order_data: dict):
        update_query = {
            "$set": {
                "updated_at": datetime.now(timezone.utc)
            }
        }

        for key, value in order_data.items():
            update_query["$set"][key] = value

        updated_result = self.orders_collection.update_one(query, update_query)

        print(f'update_order - success - {updated_result}')

    def get_order_by_order_id(self, order_id: str):
        order = self.orders_collection.find_one({"_id": ObjectId(order_id)})
        if order is None:
            print(f'get_order_by_order_id - no order found for : {order_id}')
            raise CustomException(404, "Order not found", ErrorTypesEnum.NOT_FOUND_ERROR.value)

        order = convert_object_ids_to_strings(order)
        print(f'get_order_by_order_id - success : {order}')
        return order

    def complete_order(self, driver_id: str, order_id: str):

        order = self.get_order_by_order_id(order_id)

        if order["driver_id"] != driver_id:
            print(f'complete_order - driver id mismatch')
            raise CustomException(401, "Unauthorized! Driver id mismatch!", ErrorTypesEnum.UNAUTHORIZED_ERROR.value)

        update_data = {"status": OrderStatusEnum.COMPLETED.value}

        self.update_order(order_id, update_data)

        merchant_order_service.update_merchant_orders_by_order_id(order_id, update_data)

        driver = driver_service.update_driver(driver_id, {"status": DriverStatusEnum.WAITING.value})

        print(f'complete_order - success')

        order = self.get_order_by_order_id(order_id)
        merchant_orders = merchant_order_service.get_merchant_orders_by_user_id_and_order_id(order["user_id"],
                                                                                             order_id)

        return {
            "order": order,
            "merchant_orders": merchant_orders,
            "driver": driver
        }
