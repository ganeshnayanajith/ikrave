from datetime import datetime, timezone
from bson import ObjectId

from libs.db import connect_to_mongodb
from libs.helpers import hash_password


def seed():
    print(f"... Starting DB Seed Admins ...")

    conn = connect_to_mongodb()
    db = conn.ikrave
    admins_collection = db.admins

    current_timestamp = datetime.now(tz=timezone.utc)

    admin_user = {
        "_id": ObjectId("65fd7c842313ff1fc0000000"),
        "username": "admin",
        "email": "admin@gmail.com",
        "password": hash_password("password"),
        "role": "ADMIN",
        "created_at": current_timestamp,
        "updated_at": current_timestamp
    }

    result = admins_collection.insert_one(admin_user)

    print(f"Admin data inserted: {result}")


if __name__ == "__main__":
    seed()
