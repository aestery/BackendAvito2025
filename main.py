import uvicorn
from typing import Any
from fastapi import FastAPI
from decouple import config
from app.routers.api import router
from app.models.tags import Tags
from app.services.database import db_pool
from contextlib import asynccontextmanager


tags: list[dict[str, Any]] = [
    {"name": Tags.TEAMS},
    {"name": Tags.USERS},
    {"name": Tags.PULL_REQUESTS},
    {"name": Tags.HEALTH},
]

DATABASE_URL = config("DATABASE_URL")

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.pool = await db_pool.connect(DATABASE_URL) #type: ignore
    yield
    await db_pool.close()

app = FastAPI(
    title="PR Reviewer Assignment Service",
    version="0.1.0",
    openapi_tags=tags,
    lifespan=lifespan
    )

app.include_router(router)

# For local run
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
