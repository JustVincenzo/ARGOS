from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent
ENV_PATH = PROJECT_ROOT / ".env"

load_dotenv(ENV_PATH)


def _get_bool(key: str, default: bool = False) -> bool:
    value = os.getenv(key)

    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def _get_int(key: str, default: int | None = None) -> int | None:
    value = os.getenv(key)

    if value is None or value.strip() == "":
        return default

    try:
        return int(value)
    except ValueError as exc:
        raise ValueError(f"La variable {key} debe ser un número entero.") from exc


@dataclass(frozen=True)
class Settings:
    # Discord
    token: str
    command_prefix: str

    # Dueño / desarrollo
    owner_id: int | None
    debug: bool
    debug_guild_id: int | None

    # Cogs
    cogs_folder: str

    # Base de datos
    database_url: str

    # Intents
    enable_message_content_intent: bool
    enable_member_intent: bool

    # Slash commands
    auto_sync_commands: bool
    auto_sync_global: bool

    # Logging
    log_level: str

    # Identidad visual
    bot_name: str
    embed_footer: str


def load_settings() -> Settings:
    token = os.getenv("DISCORD_TOKEN")
    database_url = os.getenv("DATABASE_URL")

    if not token:
        raise RuntimeError(
            "Falta DISCORD_TOKEN. ARGOS no puede iniciar sin token."
        )

    if not database_url:
        raise RuntimeError(
            "Falta DATABASE_URL. ARGOS necesita PostgreSQL para iniciar."
        )

    return Settings(
        token=token,
        command_prefix=os.getenv("COMMAND_PREFIX", "!"),

        owner_id=_get_int("OWNER_ID"),
        debug=_get_bool("DEBUG", False),
        debug_guild_id=_get_int("DEBUG_GUILD_ID"),

        cogs_folder=os.getenv("COGS_FOLDER", "cogs"),

        database_url=database_url,

        enable_message_content_intent=_get_bool(
            "ENABLE_MESSAGE_CONTENT_INTENT",
            False,
        ),
        enable_member_intent=_get_bool(
            "ENABLE_MEMBER_INTENT",
            False,
        ),

        auto_sync_commands=_get_bool("AUTO_SYNC_COMMANDS", True),
        auto_sync_global=_get_bool("AUTO_SYNC_GLOBAL", False),

        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),

        bot_name=os.getenv("BOT_NAME", "ARGOS"),
        embed_footer=os.getenv(
            "EMBED_FOOTER",
            "ARGOS — Observa. Registra. Actúa.",
        ),
    )


settings = load_settings()
