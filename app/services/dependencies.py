from app.services.database import pool
from app.services.team import TeamService

async def get_team_service():
    assert pool is not None
    return TeamService(pool)