from bson import ObjectId
from datetime import datetime, timezone

from libs.db import connect_to_mongodb
from libs.helpers import CustomException, convert_object_ids_to_strings
from libs.enums import ErrorTypesEnum

from src.food.service import FoodService
from src.merchant.service import MerchantService

merchant_service = MerchantService()
food_service = FoodService()


class CartService:
    def __init__(self) -> None:
        self.conn = connect_to_mongodb()
        self.db = self.conn.ikrave
        self.carts_collection = self.db.carts

    def create_cart(self, cart_data):

        current_timestamp = datetime.now(tz=timezone.utc)

        cart_data['created_at'] = current_timestamp
        cart_data['updated_at'] = current_timestamp

        cart_inserted_result = self.carts_collection.insert_one(cart_data)
        print(f'create_cart - success : {cart_inserted_result}')

        cart = self.carts_collection.find_one({"_id": cart_inserted_result.inserted_id})
        print(f'create_cart - find_one : {cart}')
        cart = convert_object_ids_to_strings(cart)

        return cart

    def add_cart_item(self, user_id: str, cart_item_data):
        cart = self.carts_collection.find_one({"user_id": ObjectId(user_id)})
        if cart is None:
            print(f'add_cart_item - failed - no cart for user_id : {user_id}')
            raise CustomException(422, "No cart found for user", ErrorTypesEnum.UNPROCESSABLE_ENTITY_ERROR.value)

        print(f'add_cart_item - starting - user_id : {user_id} cart_item_data : {cart_item_data}')

        merchant_id = cart_item_data['merchant_id']
        food_id = cart_item_data['food_id']

        merchant = merchant_service.get_merchant(merchant_id)
        if merchant is None:
            print(f'add_cart_item - failed - no merchant for merchant_id : {merchant_id}')
            raise CustomException(404, "Merchant is not found", ErrorTypesEnum.NOT_FOUND_ERROR.value)

        food_item = food_service.get_food_item_by_food_id_and_merchant_id(merchant_id, food_id)
        if food_item is None:
            print(f'add_cart_item - failed - no food for merchant_id : {merchant_id} food_id : {food_id}')
            raise CustomException(404, "Food item is not found", ErrorTypesEnum.NOT_FOUND_ERROR.value)

        matching_item = next((item for item in cart["items"] if
                              str(item["merchant_id"]) == merchant_id and
                              str(item["food_id"]) == food_id), None)

        if matching_item:
            matching_item["quantity"] += 1
            matching_item["item_total_price"] += food_item["price"]
        else:
            cart_item_data["_id"] = ObjectId()
            cart_item_data["merchant_id"] = ObjectId(cart_item_data["merchant_id"])
            cart_item_data["food_id"] = ObjectId(cart_item_data["food_id"])
            cart_item_data["quantity"] = 1
            cart_item_data["item_unit_price"] = food_item["price"]
            cart_item_data["item_total_price"] = food_item["price"]
            cart["items"].append(cart_item_data)

        filter = {
            "user_id": ObjectId(user_id)
        }

        update = {
            "$set": {
                "items": cart["items"],
                "updated_at": datetime.now(timezone.utc)
            }
        }

        updated_result = self.carts_collection.update_one(
            filter,
            update
        )

        print(f'add_cart_item - success : {updated_result}')

        cart = self.get_cart_by_user_id(user_id)

        return cart

    def remove_cart_item(self, user_id: str, data: dict):

        cart = self.carts_collection.find_one({"user_id": ObjectId(user_id)})

        if cart is None:
            print(f'remove_cart_item - failed - no cart for user_id : {user_id}')
            raise CustomException(422, "No cart found for user", ErrorTypesEnum.UNPROCESSABLE_ENTITY_ERROR.value)

        cart = convert_object_ids_to_strings(cart)

        items = cart.get("items", [])

        updated_result = None

        for item in items:
            if item["merchant_id"] == data['merchant_id'] and item["food_id"] == data['food_id']:
                if item["quantity"] > 1:

                    item_unit_price = item["item_unit_price"]

                    updated_result = self.carts_collection.update_one(
                        {
                            "_id": ObjectId(cart["_id"]),
                            "items._id": ObjectId(item["_id"])
                        },
                        {
                            "$inc": {
                                "items.$.quantity": -1,
                                "items.$.item_total_price": -item_unit_price
                            }
                        }
                    )
                else:
                    updated_result = self.carts_collection.update_one(
                        {
                            "_id": ObjectId(cart["_id"])
                        },
                        {
                            "$pull": {
                                "items": {
                                    "_id": ObjectId(item["_id"])
                                }
                            }
                        }
                    )
                break

        print(f'updated_result - success : {updated_result}')

        cart = self.get_cart_by_user_id(user_id)

        return cart

    def get_cart_items(self, user_id: str):
        cart = self.carts_collection.find_one({"user_id": ObjectId(user_id)})

        if cart is None:
            print(f'get_cart_items - no cart items for user_id : {user_id}')
            raise CustomException(422, "No cart found for user", ErrorTypesEnum.UNPROCESSABLE_ENTITY_ERROR.value)

        cart_items_formatted = convert_object_ids_to_strings(cart["items"])

        for cart_item in cart_items_formatted:
            food = food_service.get_food_item_by_food_id(cart_item['food_id'])
            cart_item['food_data'] = convert_object_ids_to_strings(food)

            merchant = merchant_service.get_merchant(cart_item['merchant_id'])
            cart_item['merchant_data'] = convert_object_ids_to_strings(merchant)

        print(f'get_cart_items - success : {cart_items_formatted}')
        return cart_items_formatted

    def get_cart_by_user_id(self, user_id: str):
        cart = self.carts_collection.find_one({"user_id": ObjectId(user_id)})
        if cart is None:
            print(f'get_cart_by_user_id - no cart for user_id : {user_id}')
            raise CustomException(422, "No cart found!", ErrorTypesEnum.UNPROCESSABLE_ENTITY_ERROR.value)

        print(f'get_cart_by_user_id - success : {cart}')
        cart = convert_object_ids_to_strings(cart)
        return cart

    def clear_cart(self, user_id: str):
        filter = {
            "user_id": ObjectId(user_id)
        }

        update = {
            "$set": {
                "items": [],
                "updated_at": datetime.now(timezone.utc)
            }
        }

        updated_result = self.carts_collection.update_one(
            filter,
            update
        )

        print(f'clear_cart - success : {updated_result}')

        cart = self.get_cart_by_user_id(user_id)

        return cart
