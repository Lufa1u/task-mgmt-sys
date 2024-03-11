
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.security import OAuth2PasswordBearer
from fastapi import APIRouter, Depends

from app.api.models.models import UserModel
from app.api.schemas.user_schemas import UserCreateSchema
from app.api.crud import user_crud
from app.core.config import get_db


user_router = APIRouter()


@user_router.get("/get_current_user")
async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="auth/login")), db: AsyncSession = Depends(get_db)):
    return await user_crud.get_current_user(token=token, db=db)


@user_router.post("/create_moderator_user")
async def create_moderator_user(user: UserCreateSchema, current_user: UserModel = Depends(get_current_user),
                                db: AsyncSession = Depends(get_db)):
    return await user_crud.create_moderator_user(user=user, current_user=current_user, db=db)


@user_router.delete("/delete_user")
async def delete_user(current_user: UserModel = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return await user_crud.delete_user(user=current_user, db=db)
