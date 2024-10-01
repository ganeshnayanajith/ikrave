from libs.db import connect_to_mongodb
from libs.enums import UserRolesEnum, ErrorTypesEnum
from libs.helpers import convert_object_ids_to_strings, compare_password, CustomException, generate_access_token


class AdminService:
    def __init__(self) -> None:
        self.conn = connect_to_mongodb()
        self.db = self.conn.ikrave
        self.admins_collection = self.db.admins

    def login_admin(self, username: str, password: str):
        admin = self.admins_collection.find_one({"username": username, "role": UserRolesEnum.ADMIN.value})

        if admin is None:
            print(f'login_admin - no admin found for {username} and {password}')
            raise CustomException(401, 'Invalid username', ErrorTypesEnum.UNAUTHORIZED_ERROR.value)

        if compare_password(password, admin['password']):
            admin = convert_object_ids_to_strings(admin)
            del admin["password"]
            access_token = generate_access_token(admin)

            print(f'login_admin - success : {admin} for {username} and {password}')

            return {
                "access_token": access_token,
                "admin": admin
            }
        else:
            raise CustomException(401, 'Invalid password', ErrorTypesEnum.UNAUTHORIZED_ERROR.value)
