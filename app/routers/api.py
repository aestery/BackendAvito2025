from fastapi import APIRouter
from app.routers import team, users, pull_requests


router = APIRouter()

router.include_router(team.router)
router.include_router(users.router)
router.include_router(pull_requests.router)