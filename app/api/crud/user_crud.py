from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api.models.models import UserModel
from app.api.schemas.user_schemas import UserCreateSchema
from app.api.auth import pwd_context, create_access_token
from app.core.config import AuthConfig


async def signup(user: UserCreateSchema, db: AsyncSession):
    rows = (await db.execute(select(UserModel.username, UserModel.email).select_from(UserModel))).all()
    all_usernames = [usernames for usernames, _ in rows]
    all_emails = [emails for _, emails in rows]
    if user.username in all_usernames or user.email in all_emails:
        raise HTTPException(status_code=409, detail="User already exist")
    new_user = UserModel(username=user.username, password_hash=pwd_context.hash(user.password), email=user.email)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def login(form_data: OAuth2PasswordRequestForm, db: AsyncSession):
    user = (await db.execute(select(UserModel).where(UserModel.username == form_data.username))).scalar_one_or_none()
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
