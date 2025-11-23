from fastapi import APIRouter
from app.routers import team, users


router = APIRouter()

router.include_router(team.router)
router.include_router(users.router)