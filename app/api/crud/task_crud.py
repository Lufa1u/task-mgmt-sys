from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy.orm import selectinload

from app.api.models.models import UserModel, TaskModel, UserRoleEnumModel, user_task_association
from app.api.schemas.task_schemas import TaskSchema, CreateTaskSchema, AssignTaskSchema, UpdateTaskSchema
from app.core.config import CustomException


async def get_task_by_id(task_id: int, db: AsyncSession):
    task = (await db.execute(select(TaskModel).where(TaskModel.id == task_id))).scalar_one_or_none()
    if not task:
        raise await CustomException.task_not_found()
    return task


async def create_task_instance(creator_user_id: int, task: CreateTaskSchema, assign_users: list[UserModel]):
    return TaskModel(
        description=task.description,
        deadline=task.deadline.date(),
        priority=task.priority,
        assigned_users=assign_users,
        creator_user_id=creator_user_id
    )


async def create_task(task: CreateTaskSchema, current_user: UserModel, db: AsyncSession):
    if current_user.role == UserRoleEnumModel.USER and task.assigned_user_ids:
        raise await CustomException.not_enough_rights()

    assign_users = [current_user]
    if task.assigned_user_ids:
        assign_users += await get_users_by_ids(task.assigned_user_ids, db=db)

    new_task = await create_task_instance(creator_user_id=current_user.id, task=task, assign_users=assign_users)
    assign_user_ids = [user.id for user in assign_users]
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    return TaskSchema(**new_task.__dict__, assigned_user_ids=assign_user_ids)


async def get_task_with_assigned_users(task_id: int, db: AsyncSession):
    task = (await db.execute(select(TaskModel).options(selectinload(TaskModel.assigned_users)).
                             where(TaskModel.id == task_id))).scalar_one_or_none()
    if not task:
        raise await CustomException.custom_exception(status_code=404, detail="Task not found")
    return task


async def get_users_by_ids(user_ids: list[int], db: AsyncSession):
    users = (await db.execute(select(UserModel).filter(UserModel.id.in_(user_ids)))).scalars().all()
    return list(users)


async def assign_task_to_users(assign_task: AssignTaskSchema, role: UserRoleEnumModel, db: AsyncSession):
    if role == UserRoleEnumModel.USER:
        raise await CustomException.not_enough_rights()

    task = await get_task_with_assigned_users(task_id=assign_task.task_id, db=db)
    task.assigned_users += await get_users_by_ids(user_ids=assign_task.assigned_user_ids, db=db)
    assigned_user_ids = [user.id for user in task.assigned_users]

    await db.commit()
    await db.refresh(task)
    return f"Task was assigned for next users: {set(assigned_user_ids)}"


async def remove_task_from_assignment_users(assign_task: AssignTaskSchema, current_user: UserModel, db: AsyncSession):
    await check_task_belongs_to_user_or_throw_exception(task_id=assign_task.task_id, user=current_user)

    result = await db.execute(delete(user_task_association).where(((user_task_association.c.user_id.in_(
        assign_task.assigned_user_ids)) &
        (user_task_association.c.task_id == assign_task.task_id) &
        (user_task_association.c.user_id != current_user.id))))

    await db.commit()
    return f"{result.rowcount} assigned users was removed"


async def check_task_belongs_to_user_or_throw_exception(task_id: int, user: UserModel):
    user_created_task_ids = [task.id for task in user.created_tasks]
    if task_id not in user_created_task_ids:
        raise await CustomException.not_enough_rights()


async def delete_task(task_id: int, current_user: UserModel, db: AsyncSession):
    await check_task_belongs_to_user_or_throw_exception(task_id=task_id, user=current_user)

    task = await get_task_by_id(task_id=task_id, db=db)
    await db.delete(task)
    await db.commit()
    return f"Task with id {task_id} was deleted"


async def update_task(new_task: UpdateTaskSchema, current_user: UserModel, db: AsyncSession):
    await check_task_belongs_to_user_or_throw_exception(task_id=new_task.id, user=current_user)

    task = await get_task_by_id(task_id=new_task.id, db=db)
    task.description = new_task.description
    task.deadline = new_task.deadline.date()
    task.priority = new_task.priority
    await db.commit()
    await db.refresh(task)
    return task
