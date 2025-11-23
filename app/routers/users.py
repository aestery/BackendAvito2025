from fastapi import APIRouter, HTTPException,Query, Depends
from models.tags import Tags
from models.error_response import ErrorCode
from services.dependencies import get_users_service
from services.users import UsersService


router = APIRouter(prefix="/users", tags=[Tags.USERS])

@router.post("/setIsActive", status_code=200)
async def set_is_active(
    user_id: str, 
    is_active: bool,
    service: UsersService = Depends(get_users_service)):
    """Установить флаг активности пользователя"""
    result, error = await service.set_is_active(user_id, is_active)

    if error == ErrorCode.NOT_FOUND:
        raise HTTPException(
            status_code=404,
            detail={
                "code": error.value,
                "message": "user with user_id is not found"
            }
        )
    
    return {"user": result}

@router.get("/getReview", status_code=200)
def get_assigned_pull_requests(
    user_id: str = Query(...),
    service: UsersService = Depends(get_users_service)):
    """Получить PR'ы, где пользователь назначен ревьювером"""
    result = service.get_reviews(user_id)

    return {"user_id": user_id, "pull_equests": result}

