from datetime import timedelta

import jwt
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from app.api.models.models import UserModel, UserRoleEnumModel
from app.api.schemas.user_schemas import UserCreateSchema, UserSchema
from app.api.auth import pwd_context, create_access_token
from app.core.config import AuthConfig
from app.celery_tasks.celery_worker import celery_app


async def get_current_user(db: AsyncSession, token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, AuthConfig.SECRET_KEY, algorithms=[AuthConfig.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError as e:
        print(e)
        raise credentials_exception

    user = (await db.execute(select(UserModel).where(UserModel.username == username))).scalar_one_or_none()
    if user is None:
        raise credentials_exception
    return UserSchema(id=user.id, username=user.username, email=user.email, role=user.user_role)


async def signup(user: UserCreateSchema, db: AsyncSession, role: UserRoleEnumModel = UserRoleEnumModel.USER):
    existing_user = (await db.execute(
        select(UserModel).filter(or_(UserModel.username == user.username,
                                     UserModel.email == user.email)))).scalar()
    if existing_user:
        if existing_user.user_role == UserRoleEnumModel.ADMIN:
            await db.delete(existing_user)
            await db.commit()
        else:
            raise HTTPException(status_code=409, detail="User already exists")
    new_user = UserModel(
        username=user.username,
        password_hash=pwd_context.hash(user.password),
        email=user.email,
        user_role=role
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserSchema(id=new_user.id, username=new_user.username, email=new_user.email, role=new_user.user_role)


async def login(form_data: OAuth2PasswordRequestForm, db: AsyncSession):
    user = (await db.execute(select(UserModel).where(UserModel.username == form_data.username))).scalar_one_or_none()
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


async def create_moderator(current_user: UserModel, user: UserCreateSchema, db: AsyncSession):
    if current_user.user_role != UserRoleEnumModel.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough rights")
    new_user = UserModel(
        username=user.username,
        password_hash=pwd_context.hash(user.password),
        email=user.email,
        user_role=UserRoleEnumModel.MODERATOR
    )
    db.add(new_user)
    await db.commit()
    return UserSchema(id=new_user.id, username=new_user.username, email=new_user.email, role=new_user.user_role)
