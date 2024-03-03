import enum

from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, Enum, Table
from sqlalchemy.orm import relationship, declarative_base


Base = declarative_base()


user_task_association = Table(
    'user_task_association', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('task_id', Integer, ForeignKey('tasks.id'))
)


class UserRoleEnumModel(enum.Enum):
    USER = 1
    MODERATOR = 2
    ADMIN = 3


class PriorityEnumModel(enum.Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True)
    email = Column(String)
    password_hash = Column(String)
    user_role = Column(Enum(UserRoleEnumModel), index=True, nullable=False)

    created_tasks = relationship("TaskModel", back_populates="creator")
    assigned_tasks = relationship("TaskModel", secondary="user_task_association", back_populates="assigned_users")


class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    deadline = Column(DateTime)
    priority = Column(Enum(PriorityEnumModel), index=True, nullable=False)

    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("UserModel", back_populates="created_tasks")

    assigned_users = relationship("UserModel", secondary="user_task_association", back_populates="assigned_tasks")
