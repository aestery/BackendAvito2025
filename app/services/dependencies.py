from services.database import db_pool
from services.team import TeamService
from services.users import UsersService
from services.pull_requests import PullRequestService

async def get_team_service():
    return TeamService(db_pool.pool)

async def get_users_service():
    return UsersService(db_pool.pool)

async def get_pull_request_service():
    return PullRequestService(db_pool.pool)