import firebase_admin
from firebase_admin import credentials, storage
from datetime import datetime
import os
from dotenv import load_dotenv

########################################################

load_dotenv()

FIREBASE_STORAGE_BUCKET_URL = os.getenv('FIREBASE_STORAGE_BUCKET_URL')


########################################################


class FirebaseStorageService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.script_dir = os.path.dirname(os.path.realpath(__file__))
        self.service_account_key_path = os.path.join(self.script_dir, "serviceAccountKey.json")
        self.cred = credentials.Certificate(self.service_account_key_path)
        firebase_admin.initialize_app(self.cred, {
            'storageBucket': FIREBASE_STORAGE_BUCKET_URL
        })
        self.bucket = storage.bucket()

    def upload_file(self, file, folder_path):
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            blob = self.bucket.blob(f'{folder_path}/{timestamp}-{file.filename}')
            blob.upload_from_file(file)
            print('upload_file - success')
            blob.make_public()
            url = blob.public_url
            print(f'upload_file - url - {url}')
            return url
        except Exception as e:
            return {'error': str(e)}
