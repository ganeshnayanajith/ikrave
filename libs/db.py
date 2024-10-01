from pymongo import MongoClient
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('../.env')
load_dotenv(dotenv_path=dotenv_path)

MONGO_DB_URI = os.getenv('MONGO_DB_URI')


class MongoDBConnection:
    _connection = None

    @classmethod
    def get_connection(cls):
        if not cls._connection:
            cls._connection = cls._create_connection()
        return cls._connection

    @classmethod
    def _create_connection(cls):
        try:
            conn = MongoClient(MONGO_DB_URI)
            print("Database connected successfully!!!")
            return conn
        except Exception as e:
            print("Could not connect to the database")
            print(e)
            return None


def connect_to_mongodb():
    return MongoDBConnection.get_connection()
