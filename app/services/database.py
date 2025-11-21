import asyncpg

pool: asyncpg.Pool | None = None

async def init_pool(dsn: str):
    global pool
    pool = await asyncpg.create_pool(dsn)

async def close_pool():
    global pool
    if pool:
        await pool.close()
        pool = None