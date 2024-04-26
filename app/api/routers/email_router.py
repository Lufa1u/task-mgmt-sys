from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.models.models import UserModel
from app.api.routers.user_router import get_current_user
from app.api.crud import email_crud
from app.core.config import get_db

email_router = APIRouter()


@email_router.post("/send_notice_to_assigned_users")
async def send_notice_to_assigned_users(assigned_user_ids: list[int],
                                        current_user: UserModel = Depends(get_current_user),
                                        db: AsyncSession = Depends(get_db)):
    return await email_crud.send_notice_to_assigned_users(assigned_user_ids=assigned_user_ids,
                                                          sender_username=current_user.username, db=db)


@email_router.get("/get_email_sending_result_by_task_id")
async def get_email_sending_result_by_task_id(task_id: str):
    return await email_crud.get_email_sending_result_by_task_id(task_id=task_id)


@email_router.get("/get_all_emails_sending_result_by_email")
async def get_email_sending_result_by_task_id(email: str):
    return await email_crud.get_all_emails_sending_result_by_email(email=email)
