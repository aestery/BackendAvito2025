import asyncpg
from asyncpg.connection import Connection
from app.models.error_response import ErrorCode
from app.models.team import Team, TeamMember

class TeamService():
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool
    
    async def add_team(self, team: Team) -> tuple[Team, ErrorCode | None]:
        async with self.pool.acquire() as connection:
            is_team = await self._team_exist(connection, team.team_name)

            if is_team:
                return (team, ErrorCode.TEAM_EXISTS)
            
            await self._insert_team(connection, team.team_name)
            
            for member in team.members:
                await self._insert_or_update_user(connection, member)
                await self._insert_member(connection, team.team_name, member)

        return team, None
    
    async def get_team(self, team_name: str) -> tuple[Team | None, ErrorCode | None]:
        async with self.pool.acquire() as connection:
            is_team = await self._team_exist(connection, team_name)

            if not is_team:
                return (None, ErrorCode.NOT_FOUND)
            
            members_rows = await self._get_team_members(connection, team_name)
            members = [
                TeamMember(
                    user_id=member['user_id'],
                    username=member['username'],
                    is_active=member['is_active']
                )
                for member in members_rows
            ]

            return (Team(team_name=team_name, members=members), None)

    async def _team_exist(self, conn: Connection, team_name: str) -> bool:
        """возвращяет наличие/отсутствие команды в бд"""
        response = await conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM teams WHERE team_name=$1)",
            team_name
        )
        return bool(response)
    
    async def _get_team_members(self, conn: Connection, team_name: str):
        """возвращает все строки с членами команды team_name"""
        return await conn.fetch(
            """
            SELECT u.user_id, u.username, u.is_active 
            FROM users u
            JOIN team_members tm
                ON tm.user_id = u.user_id
            WHERE team_name=$1
            """,
            team_name
        )

    async def _insert_team(self, conn: Connection, team_name: str):
        """добавляет комманду, возвращает статус операции"""
        return await conn.execute(
            "INSERT INTO teams (team_name) VALUES ($1)",
            team_name
        )
    
    async def _insert_member(self, conn: Connection, team_name: str, member: TeamMember):
        """добавляет участника комманды, возвращает статус операции"""
        return await conn.execute(
            """
            INSERT INTO team_members (team_name, user_id)
            VALUES ($1, $2)
            ON CONFLICT DO NOTHING
            """,
            team_name, member.user_id
        )
    
    async def _insert_or_update_user(self, conn: Connection, member: TeamMember):
        """добавляет или обновляет данные о пользователе, возвращает статус операции"""
        return await conn.execute(
            """
            INSERT INTO users (user_id, username, is_active)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO UPDATE
            SET username=EXCLUDED.username,
                is_active=EXCLUDED.is_active
            """,
            member.user_id, member.username, member.is_active
        )
