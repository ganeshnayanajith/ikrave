from datetime import datetime, timezone
from bson import ObjectId

from libs.db import connect_to_mongodb
from libs.helpers import hash_password


def seed():
    print(f"... Starting DB Seed Merchants ...")

    conn = connect_to_mongodb()
    db = conn.ikrave
    merchants_collection = db.merchants

    current_timestamp = datetime.now(tz=timezone.utc)

    common_merchant_data = {
        "password": hash_password("password"),
        "food_hygiene_rating": 4.5,
        "business_address": "Colombo",
        "opening_hours": "08:00",
        "closing_hours": "20:00",
        "geo_location": "Colombo",
        "shop_image_url": "shop_image_url",
        "is_available": True,
        "role": "MERCHANT",
        "created_by": ObjectId("65fd7c842313ff1fc0000000"),
        "created_at": current_timestamp,
        "updated_at": current_timestamp
    }

    merchants = [
        {
            "_id": ObjectId("65fd7c842313ff1fc0000001"),
            "username": "merchant1",
            "business_name": "merchant1",
            "business_registration": "merchant1",
            "phone_number": "+94776361061",
            "latitude": 51.5074,
            "longitude": -0.1278,
            **common_merchant_data
        },
        {
            "_id": ObjectId("65fd7c842313ff1fc0000002"),
            "username": "merchant2",
            "business_name": "merchant2",
            "business_registration": "merchant2",
            "phone_number": "+94776361062",
            "latitude": 53.4808,
            "longitude": -2.2426,
            **common_merchant_data
        },
        {
            "_id": ObjectId("65fd7c842313ff1fc0000003"),
            "username": "merchant3",
            "business_name": "merchant3",
            "business_registration": "merchant3",
            "phone_number": "+94776361063",
            "latitude": 52.4862,
            "longitude": -1.8904,
            **common_merchant_data
        },
        {
            "_id": ObjectId("65fd7c842313ff1fc0000004"),
            "username": "merchant4",
            "business_name": "merchant4",
            "business_registration": "merchant4",
            "phone_number": "+94776361064",
            "latitude": 55.9533,
            "longitude": -3.1883,
            **common_merchant_data
        },
        {
            "_id": ObjectId("65fd7c842313ff1fc0000005"),
            "username": "merchant5",
            "business_name": "merchant5",
            "business_registration": "merchant5",
            "phone_number": "+94776361065",
            "latitude": 55.8642,
            "longitude": -4.2518,
            **common_merchant_data
        },
        {
            "_id": ObjectId("65fd7c842313ff1fc0000006"),
            "username": "merchant6",
            "business_name": "merchant6",
            "business_registration": "merchant6",
            "phone_number": "+94776361066",
            "latitude": 51.4553,
            "longitude": -2.5966,
            **common_merchant_data
        }
    ]

    result = merchants_collection.insert_many(merchants)

    print(f"Merchants inserted: {result}")


if __name__ == "__main__":
    seed()
