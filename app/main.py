from fastapi import FastAPI

from app.api.routers.auth_router import auth_router
from app.api.routers.task_router import task_router
from app.api.routers.user_router import user_router
from app.core.config import get_db, Admin
from app.api.schemas.user_schemas import UserCreateSchema
from app.api.crud.user_crud import signup
from app.api.models.models import UserRoleEnumModel

app = FastAPI()

app.include_router(router=auth_router, prefix="/auth", tags=["AUTH"])
app.include_router(router=user_router, prefix="/users", tags=["USERS"])
app.include_router(router=task_router, prefix="/tasks", tags=["TASKS"])


@app.on_event("startup")
async def on_startup():
    async with await get_db() as db:
        admin = UserCreateSchema(username=Admin.USERNAME, password=Admin.PASSWORD,
                                 email=Admin.EMAIL)
        await signup(new_user=admin, db=db, role=UserRoleEnumModel.ADMIN)
