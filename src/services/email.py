from pathlib import Path


from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_servise
from src.conf.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=EmailStr(settings.mail_from),
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Desired Name",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Sends an email to the user with a link to confirm their email address.
    It takes in three parameters:
    -email: the user's email address, which is used as a unique identifier for them.
    -username: the username of the user who is registering. This will be displayed in their confirmation message so they know it was sent to them and not someone else.
    -host: this is where we are hosting our application, which will be used as part of our confirmation link.

    :param email: EmailStr: Specify the email address of the recipient
    :param username: str: Pass the username to the email template
    :param host: str: Pass the hostname of the server to the template
    :return: A coroutine, which is a special kind of object that can be used in an async context
    """
    try:
        token_verification = auth_servise.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email ",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        fm = FastMail(conf)
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)
