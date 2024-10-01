from bson import ObjectId
from datetime import datetime, timezone

from libs.db import connect_to_mongodb
from libs.enums import UserRolesEnum, DriverStatusEnum, ErrorTypesEnum
from libs.helpers import CustomException, compare_password, convert_object_ids_to_strings, hash_password, \
    generate_access_token
from libs.firebase_storage_service import FirebaseStorageService

from src.merchant_order.service import MerchantOrderService

firebase_storage_service = FirebaseStorageService()

merchant_order_service = MerchantOrderService()


class DriverService:
    def __init__(self) -> None:
        self.conn = connect_to_mongodb()
        self.db = self.conn.ikrave
        self.drivers_collection = self.db.drivers

    def create_driver(self, admin_id: str, driver_data: dict, photo):
        current_timestamp = datetime.now(tz=timezone.utc)

        driver_data['password'] = hash_password(driver_data['password'])
        driver_data['role'] = UserRolesEnum.DRIVER.value
        driver_data['status'] = DriverStatusEnum.WAITING.value
        driver_data['is_available'] = False
        driver_data['created_by'] = ObjectId(admin_id)
        driver_data['created_at'] = current_timestamp
        driver_data['updated_at'] = current_timestamp

        driver_inserted_result = self.drivers_collection.insert_one(driver_data)
        print(f'create_driver - success : {driver_inserted_result}')

        folder_path = f'driver/{driver_data["username"]}'

        url = firebase_storage_service.upload_file(photo, folder_path)
        print(f'create_driver - file upload success - {url}')

        driver = self.update_driver(str(driver_inserted_result.inserted_id), {'photo_url': url})
        print(f'create_driver - update_driver : {driver}')

        return driver

    def get_driver(self, driver_id: str):
        driver = self.drivers_collection.find_one({"_id": ObjectId(driver_id)})
        print(f'get_driver - success : {driver}')
        driver = convert_object_ids_to_strings(driver)
        del driver['password']
        return driver

    def update_driver(self, driver_id: str, update_data: dict):
        filter = {"_id": ObjectId(driver_id)}

        update_query = {
            "$set": {
                "updated_at": datetime.now(timezone.utc)
            }
        }

        for key, value in update_data.items():
            update_query["$set"][key] = value

        updated_result = self.drivers_collection.update_one(filter, update_query)
        print(f'update_driver - success : {updated_result}')

        driver = self.get_driver(driver_id)
        print(f'update_driver - find_one : {driver}')
        return driver

    def login_driver(self, username: str, password: str):
        driver = self.drivers_collection.find_one({"username": username, "role": UserRolesEnum.DRIVER.value})

        if driver is None:
            print(f'login_driver - no driver found for {username} and {password}')
            raise CustomException(401, 'Invalid username', ErrorTypesEnum.UNAUTHORIZED_ERROR.value)

        if compare_password(password, driver['password']):
            driver = convert_object_ids_to_strings(driver)
            del driver["password"]
            access_token = generate_access_token(driver)

            print(f'login_driver - success : {driver} for {username} and {password}')

            return {
                "access_token": access_token,
                "driver": driver
            }
        else:
            raise CustomException(401, 'Invalid password', ErrorTypesEnum.UNAUTHORIZED_ERROR.value)

    def get_available_driver_and_update(self):
        driver = self.drivers_collection.find_one({"is_available": True, "status": DriverStatusEnum.WAITING.value})

        if driver is None:
            print(f'get_available_driver_and_update - no drivers available')
            raise CustomException(404, "Drivers are not available this moment!. Try again later!",
                                  ErrorTypesEnum.NOT_FOUND_ERROR.value)

        driver = convert_object_ids_to_strings(driver)
        print(f'get_available_drivers - success : {driver}')

        updated_driver = self.update_driver(driver["_id"], {'status': DriverStatusEnum.ASSIGNED.value})
        print(f'get_available_drivers - updated_driver : {updated_driver}')
        return updated_driver
