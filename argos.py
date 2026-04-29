from __future__ import annotations

import asyncio
from pathlib import Path

import discord
from discord.ext import commands

from config import PROJECT_ROOT, settings
from logger import setup_logging

from services.database import Database
from services.prefix_manager import PrefixManager


log = setup_logging(settings.log_level)


def discover_extensions(cogs_folder: str = "cogs") -> list[str]:
    """
    Busca cogs automáticamente.

    Soporta dos estructuras:

    1. Archivo simple:
       cogs/general.py
       -> cogs.general

    2. Carpeta modular:
       cogs/general_cog/main.py
       -> cogs.general_cog.main

    Para ARGOS se recomienda la segunda estructura.
    """

    extensions: set[str] = set()
    cogs_path: Path = PROJECT_ROOT / cogs_folder

    if not cogs_path.exists():
        log.warning("No existe la carpeta de cogs: %s", cogs_path)
        return []

    for file in sorted(cogs_path.glob("*.py")):
        if file.name == "__init__.py" or file.name.startswith("_"):
            continue

        extensions.add(f"{cogs_folder}.{file.stem}")

    for main_file in sorted(cogs_path.glob("*/main.py")):
        if main_file.parent.name.startswith("_"):
            continue

        relative = main_file.relative_to(PROJECT_ROOT).with_suffix("")
        extension = ".".join(relative.parts)
        extensions.add(extension)

    return sorted(extensions)


async def dynamic_prefix(bot: commands.Bot, message: discord.Message):
    if message.guild is None:
        return commands.when_mentioned_or(settings.command_prefix)(bot, message)

    prefix_manager = getattr(bot, "prefix_manager", None)

    if prefix_manager is None:
        return commands.when_mentioned_or(settings.command_prefix)(bot, message)

    prefix = await prefix_manager.get_prefix(message.guild.id)
    return commands.when_mentioned_or(prefix)(bot, message)


class ArgosBot(commands.Bot):
    """
    Clase principal de ARGOS.

    Controla:
    - intents;
    - conexión a PostgreSQL;
    - prefijo dinámico por servidor;
    - carga de cogs;
    - sincronización de slash commands;
    - presencia del bot;
    - arranque general.
    """

    def __init__(self) -> None:
        intents = discord.Intents.default()

        intents.message_content = settings.enable_message_content_intent
        intents.members = settings.enable_member_intent

        self.database = Database(settings.database_url)
        self.prefix_manager = PrefixManager(
            database=self.database,
            default_prefix=settings.command_prefix,
        )

        super().__init__(
            command_prefix=dynamic_prefix,
            intents=intents,
            owner_id=settings.owner_id,
            help_command=None,
            allowed_mentions=discord.AllowedMentions(
                everyone=False,
                roles=False,
                users=True,
                replied_user=False,
            ),
        )

        self.initial_extensions = discover_extensions(settings.cogs_folder)

    async def setup_hook(self) -> None:
        log.info("Iniciando setup de ARGOS.")

        await self.database.connect()
        await self.database.setup_schema()

        await self.load_initial_extensions()

        if settings.auto_sync_commands:
            await self.sync_application_commands()

    async def close(self) -> None:
        await self.database.close()
        await super().close()

    async def load_initial_extensions(self) -> None:
        if not self.initial_extensions:
            log.warning("No se encontraron cogs para cargar.")
            return

        loaded = 0
        failed = 0

        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
                log.info("Cog cargado: %s", extension)
                loaded += 1
            except Exception:
                log.exception("No se pudo cargar el cog: %s", extension)
                failed += 1

        log.info(
            "Carga de cogs finalizada. Correctos: %s | Fallidos: %s",
            loaded,
            failed,
        )

    async def sync_application_commands(self) -> None:
        if settings.debug_guild_id:
            guild = discord.Object(id=settings.debug_guild_id)

            self.tree.copy_global_to(guild=guild)
            synced = await self.tree.sync(guild=guild)

            log.info(
                "Slash commands sincronizados en servidor de desarrollo %s: %s",
                settings.debug_guild_id,
                len(synced),
            )
            return

        if settings.auto_sync_global:
            synced = await self.tree.sync()

            log.info(
                "Slash commands globales sincronizados: %s",
                len(synced),
            )
            return

        log.info(
            "Sincronización global omitida. "
            "Usa AUTO_SYNC_GLOBAL=true solo cuando quieras publicar comandos globales."
        )

    async def on_ready(self) -> None:
        if self.user is None:
            log.warning("ARGOS inició, pero self.user es None.")
            return

        log.info(
            "%s conectado como %s | ID: %s",
            settings.bot_name,
            self.user,
            self.user.id,
        )

        activity = discord.Activity(
            type=discord.ActivityType.listening,
            name=f"{settings.command_prefix}ayuda",
        )

        await self.change_presence(
            status=discord.Status.online,
            activity=activity,
        )

    async def on_command_error(
        self,
        ctx: commands.Context,
        error: commands.CommandError,
    ) -> None:
        log.warning("Error en comando de prefijo: %s", error)

        embed = discord.Embed(
            title="Error",
            description="No se pudo ejecutar el comando.",
            color=discord.Color.from_rgb(220, 53, 69),
        )

        embed.set_footer(text=settings.embed_footer)

        try:
            await ctx.reply(embed=embed, mention_author=False)
        except discord.HTTPException:
            pass


async def main() -> None:
    bot = ArgosBot()

    async with bot:
        await bot.start(settings.token)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("ARGOS detenido manualmente.")
