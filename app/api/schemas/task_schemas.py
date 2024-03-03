from pydantic import BaseModel

from datetime import datetime

from app.api.models.models import PriorityEnumModel


class CreateTaskSchema(BaseModel):
    description: str
    deadline: datetime
    priority: PriorityEnumModel
    user_ids: list[int] | None = None


class TaskSchema(BaseModel):
    id: int
    description: str
    deadline: datetime
    priority: PriorityEnumModel
    assigned_users: list[int]
    creator_id: int

