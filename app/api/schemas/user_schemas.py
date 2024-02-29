from pydantic import BaseModel


class UserCreateSchema(BaseModel):
    username: str
    password: str
    email: str


class UserSchema(BaseModel):
    id: int
    username: str


