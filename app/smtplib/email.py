import smtplib

from app.core.config import SMTP


async def send_email(recipient_email, sender_username):
    text = "Hello"
    try:
        with smtplib.SMTP(SMTP.smtp_server, SMTP.smtp_port) as server:
            server.starttls()
            server.login(SMTP.SMTP_EMAIL, SMTP.SMTP_PASSWORD)
            server.sendmail(SMTP.SMTP_EMAIL, recipient_email, f'Subject:{sender_username}\n{text}')
    except smtplib.SMTPException:
        return {"email": recipient_email,
            "status": "error"}
    return {"email": recipient_email,
            "status": "success"}
