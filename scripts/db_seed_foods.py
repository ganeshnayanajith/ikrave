from datetime import datetime, timezone
from bson import ObjectId
import random

from libs.db import connect_to_mongodb
from libs.enums import CuisineTypeEnum


def seed():
    print(f"... Starting DB Seed Foods ...")

    conn = connect_to_mongodb()
    db = conn.ikrave
    foods_collection = db.foods

    current_timestamp = datetime.now(tz=timezone.utc)
    merchant_ids = [
        "65fd7c842313ff1fc0000001",
        "65fd7c842313ff1fc0000002",
        "65fd7c842313ff1fc0000003",
        "65fd7c842313ff1fc0000004",
        "65fd7c842313ff1fc0000005",
        "65fd7c842313ff1fc0000006",
    ]
    adjectives = ["Chicken", "Fish", "Veg", "Beef", "Pork", "Egg", "Sea Food", "Spicy", "Savory", "Sweet", "Tangy",
                  "Creamy", "Crunchy", "Juicy", "Zesty", "Flavorful", "Delicious"]
    nouns = ["Fried Rice", "Kottu", "Rice and Curry", "Burger", "Pizza", "Pasta", "Salad", "Sandwich", "Taco", "Curry",
             "Stir-fry", "Sushi", "Soup"]
    cuisine_types = {item.value for item in CuisineTypeEnum}

    for merchant_id in merchant_ids:
        for i in range(10):
            food_name = f"{random.choice(adjectives)} {random.choice(nouns)}"

            existing_food_names = set(food['item_name'] for food in foods_collection.find({}, {'item_name': 1}))

            if food_name in existing_food_names:
                print(f"------- Skipping duplicate food name: {food_name} -------")
                continue

            price = random.randint(100, 1000)
            rating = random.randint(1, 5)

            food = {
                "cuisine_type": random.choice(list(cuisine_types)),
                "item_name": food_name,
                "price": price,
                "is_available": True,
                "rating": rating,
                "merchant_id": ObjectId(merchant_id),
                "created_at": current_timestamp,
                "updated_at": current_timestamp,
            }

            print(f"{i} - {food_name} - inserting - merchant_id: {merchant_id}")

            result = foods_collection.insert_one(food)

            print(f"Food item inserted : {result}")


if __name__ == "__main__":
    seed()
