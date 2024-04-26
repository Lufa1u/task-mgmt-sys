import redis

from app.api.smtplib import email
from app.celery_tasks.celery_worker import celery_app
import asyncio
from app.core.config import CeleryConfig


@celery_app.task
def send_email(recipient_email, sender_username):
    result = asyncio.run(email.send_email(recipient_email, sender_username))
    return result


async def get_redis_value(key: str):
    redis_connect = await redis.asyncio.from_url(CeleryConfig.RESULT_BACKEND)
    result = await redis_connect.get(f"celery-task-meta-{key}")
    await redis_connect.close()
    return result
