from fastapi import HTTPException

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import os

from dotenv import load_dotenv


load_dotenv()


class Auth:
    SECRET_KEY = os.environ.get("SECRET_KEY")
    ALGORITHM = os.environ.get("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))


class DataBase:
    DB_USER = os.environ.get("POSTGRES_USER")
    DB_PASS = os.environ.get("POSTGRES_PASSWORD")
    DB_HOST = os.environ.get("POSTGRES_HOST")
    DB_PORT = os.environ.get("POSTGRES_PORT")
    DB_NAME = os.environ.get("POSTGRES_DB")
    DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}/{DB_NAME}"


class Admin:
    USERNAME = os.environ.get("USER_NAME")
    PASSWORD = os.environ.get("PASSWORD")
    EMAIL = os.environ.get("EMAIL")


class SMTP:
    SMTP_EMAIL = os.environ.get("SMTP_EMAIL")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587


async def get_db():
    engine = create_async_engine(DataBase.DB_URL, future=True)
    async_session = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=AsyncSession)
    async with async_session() as session:
        return session


class CustomException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

    @classmethod
    async def credentials_exception(cls):
        return cls(status_code=401, detail="Could not validate credentials")

    @classmethod
    async def not_enough_rights(cls):
        return cls(status_code=403, detail="Not enough rights")

    @classmethod
    async def incorrect_username_or_password(cls):
        return cls(status_code=400, detail="Incorrect username or password")

    @classmethod
    async def user_not_found(cls):
        return cls(status_code=404, detail="User not found")

    @classmethod
    async def user_already_exist(cls):
        return cls(status_code=409, detail="User already exists")

    @classmethod
    async def task_not_found(cls):
        return cls(status_code=404, detail="Task not found")

    @classmethod
    async def custom_exception(cls, status_code: int, detail: str):
        return cls(status_code=status_code, detail=detail)

