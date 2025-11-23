from app.services.database import db_pool
from app.services.team import TeamService
from app.services.users import UsersService

async def get_team_service():
    return TeamService(db_pool.pool)

async def get_users_service():
    return UsersService(db_pool.pool)