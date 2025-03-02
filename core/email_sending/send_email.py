from datetime import datetime
from sqlalchemy.orm import Session
from smtplib import SMTP
from email.mime.text import MIMEText
from dotenv import load_dotenv
import os
# send_email.py
# load_dotenv()

# smtp_password = os.getenv("APP_CONFIG__SMTP_PASSWORD")

def send_email(to_email, subject, body):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    from_email = os.getenv("FROM_EMAIL")
    from_password = os.getenv("SMTP_PASSWORD")
    to_email = os.getenv("TO_EMAIL")
    try:
        with SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(from_email, from_password)

            msg = MIMEText(body, "plain")
            msg["Subject"] = subject
            msg["From"] = from_email
            msg["To"] = to_email

            server.send_message(msg)
            print(f"Email отправлен на {to_email}")
    except Exception as e:
        print(f"Ошибка отправки на почту: {e}")

