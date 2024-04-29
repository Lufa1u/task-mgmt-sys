import redis
import json

from fastapi import HTTPException

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
    result = await format_redis_result(str(result))
    await redis_connect.close()
    return result


async def format_redis_result(result):
    if not result:
        raise HTTPException(status_code=404, detail="task not found")
    json_str_unescaped = result.replace('\\', '')
    all_data = json.loads(json_str_unescaped)
    status = all_data.get("status")
    result = all_data.get("result")
    date_done = all_data.get("date_done")
    return f"task status: {status}\nemail status: {result}\ndate: {date_done}"
