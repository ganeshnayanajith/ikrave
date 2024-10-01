import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

########################################################

import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('../.env')
load_dotenv(dotenv_path=dotenv_path)

SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')


########################################################

class EmailService:
    def __init__(self):
        self.smtp_username = SMTP_USERNAME
        self.smtp_password = SMTP_PASSWORD

    def send_email(self, receiver_email, subject, body):
        try:
            message = MIMEMultipart()
            message["From"] = self.smtp_username
            message["To"] = receiver_email
            message["Subject"] = subject

            message.attach(MIMEText(body, "plain"))

            session = smtplib.SMTP('smtp.gmail.com', 587)
            session.starttls()
            session.login(self.smtp_username, self.smtp_password)
            text = message.as_string()
            session.sendmail(self.smtp_username, receiver_email, text)
            session.quit()
            print("send_email - success - " + receiver_email)
        except Exception as e:
            print(f"Error sending email: {str(e)}")
