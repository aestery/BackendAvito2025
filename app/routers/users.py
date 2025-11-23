from fastapi import APIRouter, HTTPException, Depends
from app.models.tags import Tags
from app.models.user import User
from app.models.error_response import ErrorCode
from app.services.dependencies import get_users_service
from app.services.users import UsersService


router = APIRouter(prefix="/users", tags=[Tags.USERS])

@router.post("/setIsActive", status_code=200)
async def set_is_active(user_id: str, 
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

