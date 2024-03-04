from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import HTTPException
from sqlalchemy.orm import selectinload

from app.api.models.models import UserModel, TaskModel, UserRoleEnumModel
from app.api.schemas.task_schemas import TaskSchema, CreateTaskSchema, AssignTaskSchema


async def create_task(task: CreateTaskSchema, current_user: UserModel, db: AsyncSession):
    new_task = TaskModel(description=task.description, deadline=task.deadline.date(), priority=task.priority,
                         assigned_users=[current_user], creator_user_id=current_user.id)
    role = current_user.role
    current_user_id = current_user.id
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    if task.assigned_user_ids:
        assigned_user_ids = await assign_task_to_users(
            assign_task=AssignTaskSchema(task_id=new_task.id, assigned_user_ids=task.assigned_user_ids), role=role, db=db)
        if assigned_user_ids == [current_user_id]:
            raise HTTPException(status_code=400, detail="Bad user ids, users was not assigned")
    else:
        assigned_user_ids = [current_user_id]
    return TaskSchema(**new_task.__dict__, assigned_user_ids=assigned_user_ids)


async def assign_task_to_users(assign_task: AssignTaskSchema, role: UserRoleEnumModel, db: AsyncSession):
    if role == UserRoleEnumModel.USER:
        raise HTTPException(status_code=403, detail="Not enough rights")
    task = (await db.execute(select(TaskModel).options(selectinload(TaskModel.assigned_users)).
                             where(TaskModel.id == assign_task.task_id))).scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.assigned_users.extend((await db.execute(select(UserModel).filter(UserModel.id.in_(assign_task.assigned_user_ids)))).scalars().all())
    assigned_user_ids = [user.id for user in task.assigned_users]
    await db.commit()
    await db.refresh(task)
    return set(assigned_user_ids)
