from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routers.router import router
from app.core.config import get_db, AdminConfig
from app.api.schemas.user_schemas import UserCreateSchema
from app.api.crud.user_crud import signup
from app.api.models.models import UserRoleEnumModel

app = FastAPI()

app.include_router(router=router, prefix="/tasks", tags=["TASKS"])


@app.on_event("startup")
async def on_startup():
    db = await get_db()
    admin = UserCreateSchema(username=AdminConfig.USERNAME, password=AdminConfig.PASSWORD,
                             email=AdminConfig.EMAIL)
    await signup(user=admin, db=db, role=UserRoleEnumModel.ADMIN)
