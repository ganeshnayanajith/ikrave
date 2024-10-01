from libs.db import connect_to_mongodb
from datetime import datetime, timezone


def seed():
    print(f"... Starting DB Seed Pre-Set Questions ...")

    conn = connect_to_mongodb()
    db = conn.ikrave
    pre_set_questions_collection = db.pre_set_questions

    current_timestamp = datetime.now(tz=timezone.utc)

    pre_set_questions = [
        {
            "question": "What is your favorite food?",
            "created_at": current_timestamp,
            "updated_at": current_timestamp
        }
    ]

    result = pre_set_questions_collection.insert_many(pre_set_questions)

    print(f"Pre-Set questions inserted : {result}")


if __name__ == "__main__":
    seed()
