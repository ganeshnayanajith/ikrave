import firebase_admin
from firebase_admin import credentials, messaging


class FCMService:
    def __init__(self):
        self.service_account_key_path = "serviceAccountKey.json"
        self.cred = credentials.Certificate(self.service_account_key_path)
        firebase_admin.initialize_app(self.cred)

    def send_notification(self, title, body, token):
        try:

            notification = messaging.Notification(title=title, body=body)
            message_payload = messaging.Message(
                notification=notification,
                token=token,
            )

            # Send the message to the device
            response = messaging.send(message_payload)
            return {'success': True, 'response': response}
        except Exception as e:
            return {'error': str(e)}
