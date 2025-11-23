import asyncpg
from typing import NewType
from asyncpg.connection import Connection
from app.models.error_response import ErrorCode
from app.models.user import User

UsersServiceResponse = NewType(
    "UsersServiceResponse",
    tuple[User | None, ErrorCode | None])

class UsersService:
    def __init__(self, pool) -> None:
        self.pool = pool

    async def set_is_active(
            self, 
            user_id: str, 
            is_active: bool) -> UsersServiceResponse:
        
        async with self.pool.acquire() as connection:
            is_user = await self._user_exists(connection, user_id)

            if not is_user:
                return UsersServiceResponse((None, ErrorCode.NOT_FOUND))
            
            await self._set_activity(connection, user_id, is_active)
            user_info = await self._get_user(connection, user_id)

            # Костыль, чтобы закрыть None варнинг. Возвращение из этой точки не ожидается.
            if not user_info: 
                return UsersServiceResponse((None, ErrorCode.NOT_FOUND))

            user = User(
                user_id=user_id, 
                username=user_info['username'],
                team_name=user_info['team_name'],
                is_active=user_info['is_active']
                )
            
            return UsersServiceResponse((user, None))

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
        
    async def _get_user(self, conn: Connection, user_id: str) -> asyncpg.Record | None:
        return await conn.fetchrow(
            """
            SELECT users.username, users.is_active, team_members.team_name
            FROM users
            JOIN team_members
            ON users.user_id = team_members.user_id
            WHERE user_id=$1
            """,
            user_id
        )