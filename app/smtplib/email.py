import smtplib

from app.celery_tasks.celery_worker import celery_app
from app.core.config import SMTP


@celery_app.task
async def send_email(recipient_email, sender_username):
    subject = sender_username
    text = "Hello"
    try:
        with smtplib.SMTP(SMTP.smtp_server, SMTP.smtp_port) as server:
            server.starttls()
            server.login(SMTP.SMTP_EMAIL, SMTP.SMTP_PASSWORD)
            server.sendmail(SMTP.SMTP_EMAIL, recipient_email, f'Subject:{subject}\n{text}')
    except smtplib.SMTPException as e:
        raise smtplib.SMTPException(e)
