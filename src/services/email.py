from pathlib import Path

from pydantic import EmailStr
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType

from src.services.auth import auth_service
from src.conf.config import config


async def send_email(email: EmailStr, username: str, host: str) -> None:
    """
    A function that sends an email to the specified email address for verification.

    Parameters:
        email (EmailStr): The email address to send the verification email to.
        username (str): The username associated with the email address.
        host (str): The host address for the email service.

    Returns:
        None
    """
    conf = ConnectionConfig(
        MAIL_USERNAME=config.MAIL_USERNAME,
        MAIL_PASSWORD=config.MAIL_PASSWORD,
        MAIL_FROM=config.MAIL_FROM,
        MAIL_PORT=config.MAIL_PORT,
        MAIL_SERVER=config.MAIL_SERVER,
        MAIL_FROM_NAME="HW13_Test",
        MAIL_STARTTLS=False,
        MAIL_SSL_TLS=True,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER=Path('templates')
    )
    try:
        token_verification = auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Verify your email",
            recipients=[email],
            template_body={"host": host, "username": username, "email": email, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)

        await fm.send_message(message, template_name="request_verify_email.html")
    except ConnectionError as err:
        print(err)
