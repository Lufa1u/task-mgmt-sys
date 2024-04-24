from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm


from app.api.schemas.user_schemas import UserCreateSchema, UserSchema
from app.api.crud import user_crud
from app.core.config import get_db


auth_router = APIRouter()


@auth_router.post("/signup", response_model=UserSchema)
async def signup(new_user: UserCreateSchema, db: AsyncSession = Depends(get_db)):
    return await user_crud.signup(new_user=new_user, db=db)


@auth_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    return await user_crud.login(form_data=form_data, db=db)



