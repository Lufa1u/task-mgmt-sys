from datetime import timedelta

import jwt
from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import selectinload

from app.api.models.models import UserModel, UserRoleEnumModel
from app.api.schemas.user_schemas import UserCreateSchema, UserSchema
from app.api.auth import pwd_context, create_access_token
from app.core.config import Auth
from app.celery_tasks.celery_worker import celery_app


# TODO: hide password_hash!!!
async def get_current_user(db: AsyncSession, token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, Auth.SECRET_KEY, algorithms=[Auth.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = (await db.execute(select(UserModel).filter(UserModel.username == username).options(
        selectinload(UserModel.assigned_tasks),
        selectinload(UserModel.created_tasks)
    ))).scalar_one_or_none()
    if not user:
        raise credentials_exception
    return user


async def signup(user: UserCreateSchema, db: AsyncSession, role: UserRoleEnumModel = UserRoleEnumModel.USER):
    exist_user = (await db.execute(
        select(UserModel).filter(or_(UserModel.username == user.username,
                                     UserModel.email == user.email)))).scalar()
    if exist_user:
        if exist_user.role == UserRoleEnumModel.ADMIN and \
                (exist_user.username == user.username or exist_user.username == user.email):
            return
        elif exist_user.role == UserRoleEnumModel.ADMIN and \
                (exist_user.username != user.username or exist_user.username != user.email):
            await db.delete(exist_user)
        else:
            raise HTTPException(status_code=409, detail="User already exists")
    new_user = UserModel(
        username=user.username,
        password_hash=pwd_context.hash(user.password),
        email=user.email,
        role=role
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserSchema(id=new_user.id, username=new_user.username, email=new_user.email, role=new_user.role)


async def login(form_data: OAuth2PasswordRequestForm, db: AsyncSession):
    user = (await db.execute(select(UserModel).where(UserModel.username == form_data.username))).scalar_one_or_none()
    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token_expires = timedelta(minutes=Auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = await create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


async def create_moderator_user(user: UserCreateSchema, current_user: UserModel, db: AsyncSession):
    if current_user.role != UserRoleEnumModel.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough rights")

    if (await db.execute(select(UserModel).filter(or_(
            UserModel.username == user.username, UserModel.email == user.email)))).scalar():
        raise HTTPException(status_code=409, detail="User already exists")

    user = UserModel(
        username=user.username,
        password_hash=pwd_context.hash(user.password),
        email=user.email,
        role=UserRoleEnumModel.MODERATOR
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserSchema(id=user.id, username=user.username, email=user.email, role=user.role)
