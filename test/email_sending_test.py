########################################################

import os
from dotenv import load_dotenv
from pathlib import Path

from libs.email_service import EmailService

dotenv_path = Path('../.env')
load_dotenv(dotenv_path=dotenv_path)

TEST_EMAIL_RECEIVER = os.getenv('TEST_EMAIL_RECEIVER')

########################################################

email_service = EmailService()

receiver_email = TEST_EMAIL_RECEIVER
subject = "Test Email"
body = "This is a test email sent from Python!"

email_service.send_email(receiver_email, subject, body)
