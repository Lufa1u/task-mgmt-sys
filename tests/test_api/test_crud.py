from unittest.mock import AsyncMock, patch
import pytest

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.models.models import UserModel, UserRoleEnumModel
from app.api.schemas.user_schemas import UserCreateSchema, UserSchema
from app.core.config import CustomException
from app.api.crud.user_crud import (
    check_entity_or_throw_exception,
    delete_user, get_user_with_filter_or,
    create_moderator_user, get_user_by_username,
    update_user_password, check_administrator_change
)


@pytest.mark.asyncio
async def test_check_entity_or_throw_exception_exists(entity, must_exist, exception):
    entity = "entity"
    must_exist = False
    exception = CustomException(status_code=400, detail="TEST")

    with pytest.raises(CustomException):
        await check_entity_or_throw_exception(entity, must_exist, exception)


@pytest.mark.asyncio
async def test_check_entity_or_throw_exception_not_exists():
    entity = None
    must_exist = True
    exception = CustomException(status_code=400, detail="TEST")

    with pytest.raises(CustomException):
        await check_entity_or_throw_exception(entity, must_exist, exception)


async def test_get_user_by_username():
    user = UserModel(username="user", password_hash="password_hash", email="email")
    fake_db = AsyncMock()
    fake_db.execute.return_value.scalar_one_or_none.return_value = user

    result = await get_user_by_username(username="user", db=fake_db)

    assert await result == user


async def test_check_password_verify_or_throw_error():
    pass


async def test_get_current_user():
    pass


@pytest.mark.asyncio
async def test_delete_user():
    user = UserModel(username="user", email="email", role=UserRoleEnumModel.USER)
    db_mock = AsyncMock(spec=AsyncSession)

    result = await delete_user(user, db_mock)

    assert result == UserSchema(username="user", email="email", role=UserRoleEnumModel.USER)


async def test_check_administrator_change():
    user = UserModel(username="user", password_hash="password_hash", email="email", role=UserRoleEnumModel.ADMIN)
    new_user = UserCreateSchema(username="new_user", password="new_password", email="new_email")

    result = await check_administrator_change(user=user, new_user=new_user)

    assert result is True


async def test_signup():
    pass


async def test_login():
    pass


async def test_get_user_with_filter_or():
        user = UserModel(username="user", password_hash="password_hash", email="email")
        fake_db = AsyncMock()
        fake_db.execute.return_value.scalar.return_value = user
        user_variables = UserSchema(username="user", email="email")

        result = await get_user_with_filter_or(user_variables=user_variables, db=fake_db)

        assert await result == user


@pytest.mark.asyncio
async def test_create_moderator_user():
    new_user = UserCreateSchema(username="new_user", password="password", email="new_email")
    current_user = UserModel(username="admin", email="email", role=UserRoleEnumModel.ADMIN)
    db_session_mock = AsyncMock()

    with patch("app.api.crud.user_crud.check_entity_or_throw_exception", test_check_entity_or_throw_exception_exists):
        result = await create_moderator_user(new_user, current_user, db_session_mock)

    assert isinstance(result, UserSchema)
    assert result.username == new_user.username
    assert result.email == new_user.email
    assert result.role == UserRoleEnumModel.MODERATOR


@pytest.mark.asyncio
async def test_update_user_password():
    password = "password"
    user = UserModel(username="user", email="email", role=UserRoleEnumModel.USER)
    db_mock = AsyncMock(spec=AsyncSession)

    result = await update_user_password(password, user, db_mock)

    assert result == f"Password was change to: {password}"

