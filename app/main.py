from fastapi import FastAPI
from app.api.routers.router import router


app = FastAPI()

app.include_router(router=router, prefix="/tasks", tags=["TASKS"])
