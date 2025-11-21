import asyncpg
from asyncpg import UniqueViolationError
from app.models.error_response import ErrorCode
from app.models.team import Team, TeamMember

class TeamService():
    def __init__(self, pool: asyncpg.Pool) -> None:
        self.pool = pool
    
    async def add_team(self, team: Team) -> Team | ErrorCode:
        async with self.pool.acquire() as conn:
            try:
                await conn.execute(
                    "INSERT INTO teams (team_name) VALUES ($1)",
                    team.team_name,
                )
            except UniqueViolationError:
                return ErrorCode.TEAM_EXISTS

            # Upsert team members
            for member in team.members:
                await conn.execute(
                    """
                    INSERT INTO users (user_id, username, is_active)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (user_id) DO UPDATE
                    SET username=EXCLUDED.username,
                        is_active=EXCLUDED.is_active
                    """,
                    member.user_id, member.username, member.is_active
                )

                await conn.execute(
                    """
                    INSERT INTO team_members (team_name, user_id)
                    VALUES ($1, $2)
                    ON CONFLICT DO NOTHING
                    """,
                    team.team_name, member.user_id
                )

        return team