from pydantic import BaseModel

from app.api.models.models import UserRoleEnumModel


class UserCreateSchema(BaseModel):
    username: str
    password: str
    email: str


class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    role: UserRoleEnumModel


