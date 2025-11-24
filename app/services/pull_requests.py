import asyncpg
from typing import NewType
from asyncpg.connection import Connection
from app.models.error_response import ErrorCode
from app.models.pull_requests import PullRequest, PullRequestStatus


PrResponse = NewType(
    "PrResponse", 
    tuple[PullRequest | None, ErrorCode | None]
    )

class PullRequestService():
    def __init__(self, pool) -> None:
        self.pool = pool
    
    async def create_pull_request(
            self, 
            author_id: str, 
            pull_request_id: str, 
            pull_request_name: str) -> PrResponse:
        async with self.pool.acquire() as connection:
            user_exists = await self._user_exists(connection, author_id)
            team_exists = await self._team_exist(connection, author_id)

            if not user_exists or not team_exists: 
                return PrResponse((None, ErrorCode.NOT_FOUND))
            
            pr_exists = await self._pull_request_exists(connection, pull_request_id)

            if pr_exists:
                return PrResponse((None, ErrorCode.PR_EXISTS))
            
            status = PullRequestStatus.OPEN
            await self._insert_pull_request(
                connection, 
                pull_request_id, 
                pull_request_name, 
                author_id,
                status=status
                )
            
            reviewers = await self._set_revewers(
                connection, author_id, pull_request_id)
            
            pull_request = PullRequest(
                pull_request_id=pull_request_id,
                pull_request_name=pull_request_name,
                author_id=author_id,
                status=status,
                assigned_reviewer=[r['reviewer_id'] for r in reviewers]
            )

            return PrResponse((pull_request, None))
        
    async def merge_pull_request(self, pull_request_id):
        async with self.pool.acquire() as connection:
            pr_exists = await self._pull_request_exists(connection, pull_request_id)

            if not pr_exists:
                return PrResponse((None, ErrorCode.NOT_FOUND))
            
            await self._update_status_to_merged(connection, pull_request_id)
            return await self._return_pull_request(connection, pull_request_id)
    
    async def reassign_reviwer(self, pull_request_id: str, old_user_id: str):
        async with self.pool.acquire() as connection:
            pr_exists = await self._pull_request_exists(connection, pull_request_id)
            user_exists = await self._user_exists(connection, old_user_id)

            if not pr_exists or not user_exists:
                return PrResponse((None, ErrorCode.NOT_FOUND))
            
            status = await self._get_status(connection, pull_request_id)

            if status == PullRequestStatus.MERGED.value:
                return PrResponse((None, ErrorCode.PR_MERGED))
            
            is_reviewer = await self._is_reviewer(
                connection, old_user_id, pull_request_id)

            if is_reviewer == False:
                return PrResponse((None, ErrorCode.NOT_ASSIGNED))
            
            new_reviewer = await self._reassign_reviewer(
                connection, pull_request_id, old_user_id)
            
            if new_reviewer == old_user_id:
                return PrResponse((None, ErrorCode.NO_CANDIDATE))
            
            return await self._return_pull_request(connection, pull_request_id)
    
    async def _return_pull_request(
            self, conn: Connection, pull_request_id: str) -> PrResponse:
        """Возвращает пул реквест и, если не найден, ошибку"""
        request_info = await self._get_pull_request(conn, pull_request_id)
        pr_reviewers = await self._get_reviewers(conn, pull_request_id)

        if not request_info:
            return PrResponse((None, ErrorCode.NOT_FOUND))

        pull_request = PullRequest(
            pull_request_id=pull_request_id,
            pull_request_name=request_info['pull_request_name'],
            author_id=request_info['author_id'],
            status=request_info['status'],
            assigned_reviewer=[r['reviewer_id'] for r in pr_reviewers],
        )
        return PrResponse((pull_request, None))

    async def _user_exists(self, conn: Connection, user_id: str) -> bool:
        """возвращяет наличие/отсутствие пользователя в бд"""
        response = await conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM users WHERE user_id=$1)",
            user_id
        )
        return bool(response)
    
    async def _team_exist(self, conn: Connection, user_id: str) -> bool:
        """возвращяет наличие/отсутствие команды в бд"""
        response = await conn.fetchval(
            "SELECT EXISTS (SELECT team_name FROM team_members WHERE user_id=$1)",
            user_id
        )
        return bool(response)
    
    async def _pull_request_exists(self, conn: Connection, pull_request_id: str):
        """возвращяет наличие/отсутствие пул реквеста в бд"""
        response = await conn.fetchval(
            "SELECT EXISTS (SELECT 1 FROM pull_requests WHERE pull_request_id=$1)",
            pull_request_id
        )
        return bool(response)   
    
    async def _is_reviewer(
            self, conn: Connection, user_id: str, pull_request_id: str):
        """сообщает является ли пользователь ревьюером выбранного реквеста"""
        status = await conn.fetchval(
            """
            SELECT EXISTS (
                SELECT 1 
                FROM pull_request_reviewers
                WHERE pull_request_id=$1
                    AND reviewer_id=$2
            )
            """,
            pull_request_id, user_id
        )

        return status
    
    async def _get_status(self, conn: Connection, pull_request_id):
        """получить статус функции"""
        status = await conn.fetchval(
            """
            SELECT status
            FROM pull_requests
            WHERE pull_request_id=$1
            """,
            pull_request_id
        )

        return status

    async def _get_reviewers(self, conn: Connection, pull_request_id: str):
        return await conn.fetch(
            """
            SELECT reviewer_id 
            FROM pull_request_reviewers 
            WHERE pull_request_id=$1
            """,
            pull_request_id
        )
    
    async def _get_pull_request(self, conn: Connection, pull_request_id: str):
        """получить полную информацию о pr"""
        return await conn.fetchrow(
            """
            SELECT 
                pr.pull_request_name,
                pr.author_id,
                pr.status,
                pr.created_at,
                pr.merged_at
            FROM pull_requests pr
            LEFT JOIN pull_request_reviewers r
                ON pr.pull_request_id = r.pull_request_id
            WHERE pr.pull_request_id=$1
            GROUP BY
                pr.pull_request_id,
                pr.pull_request_name,
                pr.author_id,
                pr.status,
                pr.created_at,
                pr.merged_at
            """,
            pull_request_id
        )

    async def _insert_pull_request(
            self, 
            conn: Connection,
            pull_request_id: str, 
            pull_request_name: str,
            author_id: str,
            status: PullRequestStatus
            ):
        """добавляет пулл реквест в бд"""
        await conn.execute(
            """
            INSERT INTO pull_requests
            (pull_request_id, pull_request_name, author_id, status)
            VALUES ($1, $2, $3, $4)
            """,
            pull_request_id, pull_request_name, author_id, status.value
        )
    
    async def _update_status_to_merged(
            self, conn: Connection, pull_request_id: str):
        """изменяеит статус пул реквеста на MERGED"""
        await conn.execute(
            """
            UPDATE pull_requests
            SET status=$1, merged_at=NOW()
            WHERE pull_request_id=$2
                AND status != $1
            """,
            PullRequestStatus.MERGED.value, pull_request_id
        )

    async def _set_revewers(
            self,
            conn: Connection,
            pr_author_id: str,
            pull_request_id: str,
            limit: int = 2
            ) -> list[asyncpg.Record]: 
        return await conn.fetch(
            """
            INSERT INTO pull_request_reviewers (pull_request_id, reviewer_id)
            SELECT $1, tm2.user_id
            FROM team_members tm
            JOIN team_members tm2
                ON tm.team_name = tm2.team_name
            JOIN users u
                ON tm2.user_id = u.user_id
            WHERE tm.user_id = $2          
                AND tm2.user_id != $2        
                AND u.is_active = TRUE
            LIMIT $3     
            RETURNING reviewer_id                 
            """,
            pull_request_id, pr_author_id, limit
        )
    
    async def _reassign_reviewer(
            self, 
            conn: Connection,     
            pull_request_id: str, 
            old_user_id: str):
        return await conn.fetchval(
            """
            UPDATE pull_request_reviewers r
            SET reviewer_id = COALESCE(
                (
                SELECT tm.user_id
                FROM team_members tm
                JOIN team_members tm2
                    ON tm.team_name = tm2.team_name
                JOIN users u
                    ON tm2.user_id = u.user_id
                LEFT JOIN pull_request_reviewers prr
                    ON tm2.user_id = prr.reviewer_id
                LEFT JOIN pull_requests pr
                    ON prr.pull_request_id = pr.pull_request_id
                WHERE prr.pull_request_id = $1
                    AND tm2.user_id != $2
                    AND tm.user_id != $2
                    AND tm.user_id != pr.author_id
                    AND tm.user_id != prr.reviewer_id
                ORDER BY RANDOM()
                LIMIT 1
                ),
                $2
            )
            WHERE r.pull_request_id=$1
                AND r.reviewer_id=$2
            RETURNING reviewer_id
            """,
            pull_request_id, old_user_id
        )
