from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, Enum, DateTime, ForeignKey
import enum

Base = declarative_base()


class PriorityEnum(enum.Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    tasks = relationship("Tasks", back_populates="user")


class Tasks(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    deadline = Column(DateTime)
    priority = Column(Enum(PriorityEnum), index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("UserModel", back_populates="tasks")

