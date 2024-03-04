from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from app.api.crud import task_crud
from app.api.models.models import UserModel
from app.api.schemas.user_schemas import UserCreateSchema, UserSchema
from app.api.schemas.task_schemas import CreateTaskSchema, AssignTaskSchema
from app.api.crud import user_crud
from app.core.config import get_db


router = APIRouter()


@router.post("/signup", response_model=UserSchema)
async def signup(user: UserCreateSchema, db: AsyncSession = Depends(get_db)):
    return await user_crud.signup(user=user, db=db)


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    return await user_crud.login(form_data=form_data, db=db)


@router.get("/get_current_user")
async def get_current_user(token: str = Depends(OAuth2PasswordBearer(tokenUrl="tasks/login")), db: AsyncSession = Depends(get_db)):
    return await user_crud.get_current_user(token=token, db=db)


@router.post("/create_moderator_user")
async def create_moderator_user(user: UserCreateSchema, current_user: UserModel = Depends(get_current_user),
                                db: AsyncSession = Depends(get_db)):
    return await user_crud.create_moderator_user(user=user, current_user=current_user, db=db)


@router.post("/create_task")
async def create_task(task: CreateTaskSchema, current_user: UserModel = Depends(get_current_user),
                      db: AsyncSession = Depends(get_db)):
    return await task_crud.create_task(task=task, current_user=current_user, db=db)


@router.post("/assign_task_to_users", status_code=200)
async def assign_task_to_users(assign_task: AssignTaskSchema, current_user: UserModel = Depends(get_current_user),
                               db: AsyncSession = Depends(get_db)):
    return await task_crud.assign_task_to_users(assign_task=assign_task, role=current_user.role, db=db)



