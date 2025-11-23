from app.services.database import db_pool
from app.services.team import TeamService
from app.services.users import UsersService
from app.services.pull_requests import PullRequestService

async def get_team_service():
    return TeamService(db_pool.get_pool)

async def get_users_service():
    return UsersService(db_pool.get_pool)

async def get_pull_request_service():
    return PullRequestService(db_pool.get_pool)