from __future__ import annotations

import asyncpg


class Database:
    """
    Capa mínima de conexión a PostgreSQL para ARGOS.

    Maneja:
    - conexión por pool;
    - cierre limpio;
    - creación de tablas base.
    """

    def __init__(self, database_url: str) -> None:
        self.database_url = database_url
        self.pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        self.pool = await asyncpg.create_pool(
            dsn=self.database_url,
            min_size=1,
            max_size=5,
        )

    async def close(self) -> None:
        if self.pool is not None:
            await self.pool.close()
            self.pool = None

    def get_pool(self) -> asyncpg.Pool:
        if self.pool is None:
            raise RuntimeError("La base de datos no está conectada.")

        return self.pool

    async def setup_schema(self) -> None:
        pool = self.get_pool()

        async with pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS guild_prefixes (
                    guild_id BIGINT PRIMARY KEY,
                    prefix VARCHAR(5) NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                );
                """
            )
