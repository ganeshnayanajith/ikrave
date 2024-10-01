from datetime import datetime, timezone
from bson import ObjectId

from libs.db import connect_to_mongodb
from libs.helpers import hash_password


def seed():
    print(f"... Starting DB Seed Users ...")

    conn = connect_to_mongodb()
    db = conn.ikrave
    users_collection = db.users
    carts_collection = db.carts

    current_timestamp = datetime.now(tz=timezone.utc)

    user = {
        "_id": ObjectId("65fd7c842313ff1fc1000000"),
        "full_name": "user1",
        "username": "user1",
        "email": "user1@gmail.com",
        "password": hash_password("password"),
        "address": "Colombo",
        "preferences": [],
        "role": "USER",
        "device_token": "",
        "created_at": current_timestamp,
        "updated_at": current_timestamp
    }

    cart = {
        "_id": ObjectId("65fd7c842313ff1fc2000000"),
        "items": [],
        "user_id": ObjectId("65fd7c842313ff1fc1000000"),
        "created_at": current_timestamp,
        "updated_at": current_timestamp
    }

    user_inserted_result = users_collection.insert_one(user)
    cart_inserted_result = carts_collection.insert_one(cart)

    print(f"User inserted : {user_inserted_result}")
    print(f"Cart inserted : {cart_inserted_result}")


if __name__ == "__main__":
    seed()
