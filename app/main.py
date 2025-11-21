import uvicorn
from typing import Any
from fastapi import FastAPI
from app.routers.api import router
from app.models.tags import Tags
from app.services.database import init_pool, close_pool
from contextlib import asynccontextmanager


tags: list[dict[str, Any]] = [
    {"name": Tags.TEAMS},
    {"name": Tags.USERS},
    {"name": Tags.PULL_REQUESTS},
    {"name": Tags.HEALTH},
]

#TODO: move to .env
DATABASE_URL = "postgresql://postgres@localhost/postgres"

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool(DATABASE_URL)
    yield
    await close_pool()

app = FastAPI(
    title="PR Reviewer Assignment Service",
    version="0.0.1",
    openapi_tags=tags,
    lifespan=lifespan
    )

app.include_router(router)

# For local run
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
