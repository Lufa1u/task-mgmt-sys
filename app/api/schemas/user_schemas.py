from pydantic import BaseModel

from app.api.models.models import UserRoleEnumModel


class UserCreateSchema(BaseModel):
    username: str
    password: str
    email: str


class UserSchema(BaseModel):
    id: int | None = None
    username: str | None = None
    email: str | None = None
    role: UserRoleEnumModel | None = None



