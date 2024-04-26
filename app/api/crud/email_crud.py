import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.celery_tasks import tasks as celery_tasks
from app.api.crud.task_crud import get_users_by_ids


async def create_task_id(assigned_user_email: str):
    return f"{assigned_user_email}_{uuid.uuid4()}"


async def send_notice_to_assigned_users(assigned_user_ids: list[int], sender_username: str, db: AsyncSession):
    result = []
    assigned_users = await get_users_by_ids(user_ids=assigned_user_ids, db=db)
    for assigned_user in assigned_users:
        task_id = await create_task_id(assigned_user_email=assigned_user.email)
        task_id = celery_tasks.send_email.apply_async(args=(assigned_user.email, sender_username), task_id=task_id)
        result.append(str(task_id))
    return f"Created {len(result)} tasks. Task IDs: {result}"


async def get_email_sending_result_by_task_id(task_id: str):
    return await celery_tasks.get_redis_value(task_id)


async def get_all_emails_sending_result_by_email(email: str):
    return await celery_tasks.get_redis_value(f"{email}_*")
