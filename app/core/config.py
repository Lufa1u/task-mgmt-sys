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


async def get_db():
    engine = create_async_engine(DataBase.DB_URL, future=True)
    async_session = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=AsyncSession)
    async with async_session() as session:
        return session
