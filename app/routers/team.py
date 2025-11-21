from fastapi import APIRouter, Depends
from app.models.tags import Tags
from app.models.team import Team
from app.services.dependencies import get_team_service
from app.services.team import TeamService


router = APIRouter(prefix="/team", tags=[Tags.TEAMS])

@router.post("/add")
async def create_team(body: Team, service: TeamService = Depends(get_team_service)):
    '''Создать команду с участниками (создаёт/обновляет пользователей)'''
    result = await service.add_team(body)