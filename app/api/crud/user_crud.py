from datetime import timedelta

import jwt

from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from fastapi.security import OAuth2PasswordRequestForm

from app.api.models.models import UserModel, UserRoleEnumModel
from app.api.schemas.user_schemas import UserCreateSchema, UserSchema
from app.api.auth import pwd_context, create_access_token
from app.core.config import Auth, CustomException
from app.celery_tasks.celery_worker import celery_app


async def check_entity_or_throw_exception(entity: any, must_exist: bool, exception: CustomException):
    if must_exist:
        if not entity:
            raise exception
        else:
            return
    if entity:
        raise exception


async def get_username_using_token(token: str):
    try:
        payload = jwt.decode(token, Auth.SECRET_KEY, algorithms=[Auth.ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError as exception:
        raise exception


async def get_user_by_username(username: str, db: AsyncSession):
    return (await db.execute(select(UserModel).filter(UserModel.username == username).options(
        selectinload(UserModel.assigned_tasks),
        selectinload(UserModel.created_tasks)
    ))).scalar_one_or_none()


async def check_password_verify_or_throw_error(password: str, hash: str, exception: CustomException):
    if not pwd_context.verify(password, hash):
        raise exception


# TODO: hide password_hash!!!
async def get_current_user(db: AsyncSession, token: str):
    username = await get_username_using_token(token=token)
    await check_entity_or_throw_exception(entity=username, must_exist=True, exception=await CustomException.credentials_exception())
    user = await get_user_by_username(username=username, db=db)
    await check_entity_or_throw_exception(entity=user, must_exist=True, exception=await CustomException.user_not_found())
    return user


async def delete_user(user: UserModel, db: AsyncSession):
    await db.delete(user)
    await db.commit()
    return UserSchema(**user.__dict__)


async def check_administrator_change(user: UserModel, new_user: UserCreateSchema):
    if user.role == UserRoleEnumModel.ADMIN and (user.username != new_user.username or user.email != new_user.email):
        return True


async def signup(new_user: UserCreateSchema, db: AsyncSession, role: UserRoleEnumModel = UserRoleEnumModel.USER):
    exist_user = await get_user_with_filter_or(UserSchema(username=new_user.username, email=new_user.email), db=db)
    # TODO: баг с заменой админа на 104
    if role == UserRoleEnumModel.ADMIN and exist_user:
        if not await check_administrator_change(user=exist_user, new_user=new_user):
            return UserSchema(**exist_user.__dict__)
        await delete_user(exist_user, db=db)
    await check_entity_or_throw_exception(entity=exist_user, must_exist=False, exception=await CustomException.user_already_exist())

    new_user = UserModel(
        username=new_user.username,
        password_hash=pwd_context.hash(new_user.password),
        email=new_user.email,
        role=role
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return UserSchema(id=new_user.id, username=new_user.username, email=new_user.email, role=new_user.role)


async def login(form_data: OAuth2PasswordRequestForm, db: AsyncSession):
    user = await get_user_by_username(username=form_data.username, db=db)

    await check_entity_or_throw_exception(entity=user, must_exist=True, exception=await CustomException.user_not_found())
    await check_password_verify_or_throw_error(password=form_data.password, hash=user.password_hash,
                                               exception=await CustomException.incorrect_username_or_password())

    access_token = await create_access_token(data={"sub": user.username}, expires_delta=timedelta(minutes=Auth.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}


async def get_user_with_filter_or(user_variables: UserSchema, db: AsyncSession):
    return (await db.execute(select(UserModel).filter(or_(
        UserModel.username == user_variables.username,
        UserModel.email == user_variables.email, UserModel.id == user_variables.id,
        UserModel.role == user_variables.role)))).scalar()


async def create_moderator_user(user: UserCreateSchema, current_user: UserModel, db: AsyncSession):
    if current_user.role != UserRoleEnumModel.ADMIN:
        raise await CustomException.not_enough_rights()

    user_in_database = await get_user_with_filter_or(UserSchema(username=user.username, email=user.email), db=db)
    await check_entity_or_throw_exception(entity=user_in_database, must_exist=False, exception=await CustomException.user_already_exist())

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


async def update_user(user_schema: UserSchema, current_user: UserModel, db: AsyncSession):
    pass
