from libs.db import connect_to_mongodb


def seed():
    print(f"... Starting DB Seed Indexes ...")

    conn = connect_to_mongodb()
    db = conn.ikrave

    users_collection = db.users
    users_collection.create_index([('username', 1)], unique=True)
    users_collection.create_index([('email', 1)], unique=True)
    users_collection.create_index(
        [('phone_number', 1)],
        unique=True,
        partialFilterExpression={'phone_number': {'$exists': True}}
    )

    admins_collection = db.admins
    admins_collection.create_index([('username', 1)], unique=True)
    admins_collection.create_index([('email', 1)], unique=True)

    pre_set_questions_collection = db.pre_set_questions
    pre_set_questions_collection.create_index([('question', 1)], unique=True)

    carts_collection = db.carts
    carts_collection.create_index([('user_id', 1)], unique=True)

    merchant_requests_collection = db.merchant_requests
    merchant_requests_collection.create_index([('username', 1)], unique=True)
    merchant_requests_collection.create_index([('business_name', 1)], unique=True)
    merchant_requests_collection.create_index([('business_registration', 1)], unique=True)
    merchant_requests_collection.create_index([('phone_number', 1)], unique=True)

    merchants_collection = db.merchants
    merchants_collection.create_index([('username', 1)], unique=True)
    merchants_collection.create_index([('business_name', 1)], unique=True)
    merchants_collection.create_index([('business_registration', 1)], unique=True)
    merchants_collection.create_index([('phone_number', 1)], unique=True)

    foods_collection = db.foods
    foods_collection.create_index(
        [('merchant_id', 1), ('item_name', 1)],
        unique=True,
    )

    drivers_collection = db.drivers
    drivers_collection.create_index([('full_name', 1)], unique=True)
    drivers_collection.create_index([('username', 1)], unique=True)

    print(f"Indexes created successfully")


if __name__ == "__main__":
    seed()
