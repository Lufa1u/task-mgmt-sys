from app.smtplib import email
from app.celery_tasks.celery_worker import celery_app
import asyncio


@celery_app.task
def send_email(recipient_email, sender_username):
    result = asyncio.run(email.send_email(recipient_email, sender_username))
    return result
