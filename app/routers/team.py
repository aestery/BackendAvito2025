from fastapi import APIRouter, HTTPException, Query, Depends
from app.models.tags import Tags
from app.models.team import Team
from app.models.error_response import ErrorCode
from app.services.dependencies import get_team_service
from app.services.team import TeamService


router = APIRouter(prefix="/team", tags=[Tags.TEAMS])

@router.post("/add", status_code=201)
async def create_team(body: Team, 
                      service: TeamService = Depends(get_team_service)):
    '''Создать команду с участниками (создаёт/обновляет пользователей)'''
    result, error = await service.add_team(body)

    if error == ErrorCode.TEAM_EXISTS:
        raise HTTPException(
            status_code=400,
            detail={
                "code": error.value,
                "message": "team_name already exists"
            }
        )
    
    return {"team": result}

@router.get("/get", status_code=200)
async def get_team(team_name: str = Query(...),
                   service: TeamService = Depends(get_team_service)):
    """Получить команду с участниками"""
    result, error = await service.get_team(team_name)

    if error == ErrorCode.NOT_FOUND:
        raise HTTPException(
            status_code=404,
            detail={
                "code": error.value,
                "message": "team_name not found"
            }
        )
    
    return {"team": result}
