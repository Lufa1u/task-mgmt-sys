from fastapi import FastAPI
from api.routers.router import router


app = FastAPI()

app.include_router(router=router, prefix="/tasks", tags=["TASKS"])
