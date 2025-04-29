from email.message import EmailMessage
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi import BackgroundTasks
from app.core.config import settings 
from pathlib import Path

conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_FROM= settings.EMAIL_FROM,
    MAIL_PORT = settings.SMTP_PORT,
    MAIL_SERVER = settings.SMTP_SERVER,
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    MAIL_FROM_NAME="Desired Name",
    TEMPLATE_FOLDER = Path(__file__).parent / "templates" / "email"
)

def send_registration_email(background_tasks: BackgroundTasks, to_email: str, body: dict):
    
    print(f"Password: {repr(settings.SMTP_PASSWORD)}")
    message = MessageSchema(
        subject="Registration",
        recipients=[to_email],
        template_body=body,
        subtype=MessageType.html)

    fm = FastMail(conf)
    background_tasks.add_task(
        fm.send_message, message, template_name='registration.html')
    
def send_forgot_password_email(background_tasks: BackgroundTasks, to_email: str, body: dict):
    
    print(f"Password: {repr(settings.SMTP_PASSWORD)}")
    message = MessageSchema(
        subject="Forgot Password",
        recipients=[to_email],
        template_body=body,
        subtype=MessageType.html)

    fm = FastMail(conf)
    background_tasks.add_task(
        fm.send_message, message, template_name='forgotPassword.html')
