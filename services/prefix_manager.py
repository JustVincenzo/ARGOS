from __future__ import annotations

from services.database import Database


class PrefixManager:
    def __init__(self, database: Database, default_prefix: str) -> None:
        self.database = database
        self.default_prefix = default_prefix
        self.cache: dict[int, str] = {}

    async def get_prefix(self, guild_id: int) -> str:
        if guild_id in self.cache:
            return self.cache[guild_id]

        pool = self.database.get_pool()

        async with pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT prefix
                FROM guild_prefixes
                WHERE guild_id = $1;
                """,
                guild_id,
            )

        if row is None:
            return self.default_prefix

        prefix = str(row["prefix"])
        self.cache[guild_id] = prefix
        return prefix

    async def set_prefix(self, guild_id: int, prefix: str) -> None:
        prefix = self.validate_prefix(prefix)

        pool = self.database.get_pool()

        async with pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO guild_prefixes (guild_id, prefix, updated_at)
                VALUES ($1, $2, NOW())
                ON CONFLICT (guild_id)
                DO UPDATE SET
                    prefix = EXCLUDED.prefix,
                    updated_at = NOW();
                """,
                guild_id,
                prefix,
            )

        self.cache[guild_id] = prefix

    async def reset_prefix(self, guild_id: int) -> None:
        pool = self.database.get_pool()

        async with pool.acquire() as conn:
            await conn.execute(
                """
                DELETE FROM guild_prefixes
                WHERE guild_id = $1;
                """,
                guild_id,
            )

        self.cache.pop(guild_id, None)

    def validate_prefix(self, prefix: str) -> str:
        prefix = prefix.strip()

        if not prefix:
            raise ValueError("El prefijo no puede estar vacío.")

        if len(prefix) > 5:
            raise ValueError("El prefijo no puede tener más de 5 caracteres.")

        if any(char.isspace() for char in prefix):
            raise ValueError("El prefijo no puede contener espacios.")

        return prefix
