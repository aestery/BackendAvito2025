import asyncpg
from typing import NewType
from asyncpg.connection import Connection
from app.models.error_response import ErrorCode
from app.models.user import User
from app.models.user import UserStatusUpdate
from app.models.pull_requests import PullRequestShort

UsersServiceResponse = NewType(
    "UsersServiceResponse",
    tuple[User | None, ErrorCode | None])

class UsersService:
    def __init__(self, pool) -> None:
        self.pool = pool

    async def set_is_active(
            self, 
            user_status: UserStatusUpdate
            ) -> UsersServiceResponse:
        async with self.pool.acquire() as connection:
            is_user = await self._user_exists(connection, user_status.user_id)

            if not is_user:
                return UsersServiceResponse((None, ErrorCode.NOT_FOUND))
            
            await self._set_activity(
                connection, user_status.user_id, user_status.is_active)
            user_info = await self._get_user(connection, user_status.user_id)

            # Костыль, чтобы закрыть None варнинг. Возвращение из этой точки не ожидается.
            if not user_info: 
                return UsersServiceResponse((None, ErrorCode.NOT_FOUND))

            user = User(
                user_id=user_status.user_id, 
                username=user_info['username'],
                team_name=user_info['team_name'],
                is_active=user_info['is_active']
                )
            
            return UsersServiceResponse((user, None))

    async def get_reviews(self, user_id: str):
        async with self.pool.acquire() as connection:
            response = await self._get_pull_requests(connection, user_id)
            pull_requests = []

            for pr in response:
                pull_requests.append(
                    PullRequestShort(
                        pull_request_id=pr['pull_request_id'],
                        pull_request_name=pr['pull_request_name'],
                        author_id=pr['author_id'],
                        status=pr['status']
                    )
                )
                
            return pull_requests

    async def _user_exists(self, conn: Connection, user_id: str) -> bool:
        """возвращяет наличие/отсутствие пользователя в бд"""
        response = await conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM users WHERE user_id=$1)",
            user_id
        )
        return bool(response)
    
    async def _set_activity(self, conn: Connection, user_id: str, is_active: bool):
        """обновляет параметр is_active пользователя user_id"""
        await conn.execute(
            """
            UPDATE users 
            SET is_active=$1 
            WHERE user_id=$2
            """,
            is_active, user_id
        )
        
    async def _get_user(
            self, conn: Connection, user_id: str
            ) -> asyncpg.Record | None:
        return await conn.fetchrow(
            """
            SELECT u.username, u.is_active, tm.team_name
            FROM users u
            JOIN team_members tm
                ON u.user_id = tm.user_id
            WHERE u.user_id=$1
            """,
            user_id
        )
    
    async def _get_pull_requests(self, conn: Connection, user_id: str):
        """получить полную информацию о pr"""
        return await conn.fetch(
            """
            SELECT 
                pr.pull_request_id,
                pr.pull_request_name,
                pr.author_id,
                pr.status
            FROM pull_requests pr
            JOIN pull_request_reviewers prr
                ON pr.pull_request_id = prr.pull_request_id
            WHERE prr.reviewer_id=$1
            """,
            user_id
        )