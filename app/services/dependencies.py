from app.services.database import db_pool
from app.services.team import TeamService

async def get_team_service():
    return TeamService(db_pool.pool)