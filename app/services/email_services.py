from fastapi_mail import ConnectionConfig
from fastapi_mail import FastMail
from fastapi_mail import MessageSchema


async def send_verification_email(
    email: str,
    verification_link: str
):

    conf = ConnectionConfig(
        MAIL_USERNAME="rinkal.anblick@gmail.com",
        MAIL_PASSWORD="haav yytw mzkx qcnx",
        MAIL_FROM="rinkal.anblick@gmail.com",
        MAIL_PORT=587,
        MAIL_SERVER="smtp.gmail.com",
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
    )

    message = MessageSchema(
        subject="Verify Your Email",
        recipients=[email],
        body=f"""
        <h2>Email Verification</h2>

        <p>
            Click below to verify your account
        </p>

        <a href="{verification_link}">
            Verify Email
        </a>
        """,
        subtype="html",
    )

    fm = FastMail(conf)

    await fm.send_message(message)