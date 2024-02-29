import enum

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String)
    password_hash = Column(String)
    tasks = relationship("TaskModel", back_populates="user")


class PriorityEnumModel(enum.Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    deadline = Column(DateTime)
    priority = Column(Enum(PriorityEnumModel), index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserModel", back_populates="tasks")
