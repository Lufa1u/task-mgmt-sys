from pydantic import BaseModel

from datetime import datetime

from app.api.models.models import PriorityEnumModel


class CreateTaskSchema(BaseModel):
    description: str
    deadline: datetime
    priority: PriorityEnumModel
    assigned_user_ids: list[int] | None = None


class TaskSchema(BaseModel):
    id: int
    description: str
    deadline: datetime
    priority: PriorityEnumModel
    assigned_user_ids: list[int]
    creator_user_id: int


class AssignTaskSchema(BaseModel):
    task_id: int
    assigned_user_ids: list[int]

