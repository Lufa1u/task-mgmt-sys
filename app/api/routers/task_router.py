from fastapi import Depends, APIRouter

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.crud import task_crud
from app.api.models.models import UserModel
from app.api.routers.user_router import get_current_user
from app.api.schemas.task_schemas import CreateTaskSchema, AssignTaskSchema
from app.core.config import get_db


task_router = APIRouter()


@task_router.get("/get_task_by_id")
async def get_task_by_id(task_id: int, db: AsyncSession = Depends(get_db)):
    return await task_crud.get_task_by_id(task_id=task_id, db=db)


@task_router.post("/create_task")
async def create_task(task: CreateTaskSchema, current_user: UserModel = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    return await task_crud.create_task(task=task, current_user=current_user, db=db)


@task_router.post("/assign_task_to_users", status_code=200)
async def assign_task_to_users(assign_task: AssignTaskSchema, current_user: UserModel = Depends(get_current_user),
                               db: AsyncSession = Depends(get_db)):
    return await task_crud.assign_task_to_users(assign_task=assign_task, role=current_user.role, db=db)


@task_router.delete("/delete_task")
async def delete_task(task_id: int, current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await task_crud.delete_task(task_id=task_id, current_user=current_user, db=db)
