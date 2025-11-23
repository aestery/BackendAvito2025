import asyncpg

class DBPool:
    @property
    def get_pool(self) -> asyncpg.Pool:
        return self.pool

    async def connect(self, dsn: str):
        if self.pool == None: 
            self.pool: asyncpg.Pool = await asyncpg.create_pool(dsn)

    async def close(self):
        if self.pool: 
            await self.pool.close()

db_pool = DBPool()