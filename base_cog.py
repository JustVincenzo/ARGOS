from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import TYPE_CHECKING

import discord
from discord.ext import commands

from config import settings
from logger import get_logger

if TYPE_CHECKING:
    from argos import ArgosBot


class ArgosColors:
    """
    Paleta oficial de ARGOS.

    ROJO:
        Advertencias, errores, alertas, urgencias y acciones críticas.

    NARANJO:
        Logs, información especial, avisos administrativos y eventos relevantes.

    AZUL:
        Comandos normales, respuestas generales y embeds estándar.

    GRIS:
        Reservado. Por ahora se usa para estados neutrales o información sin categoría.
    """

    RED = discord.Color.from_rgb(220, 53, 69)
    ORANGE = discord.Color.from_rgb(255, 152, 0)
    BLUE = discord.Color.from_rgb(52, 120, 246)
    GRAY = discord.Color.from_rgb(108, 117, 125)


class BaseCog(commands.Cog):
    """
    Clase base para todos los cogs de ARGOS.

    Su función es mantener una identidad común entre módulos:
    - logger propio;
    - embeds estandarizados;
    - respuestas en español;
    - colores coherentes;
    - utilidades comunes para interacciones.
    """

    module_name: str = "Base"

    def __init__(self, bot: "ArgosBot") -> None:
        self.bot = bot
        self.log: logging.Logger = get_logger(self.module_name)

    async def cog_load(self) -> None:
        self.log.info("Cog cargado.")

    async def cog_unload(self) -> None:
        self.log.info("Cog descargado.")

    # ============================================================
    # EMBEDS BASE
    # ============================================================

    def make_embed(
        self,
        title: str,
        description: str | None = None,
        *,
        color: discord.Color = ArgosColors.BLUE,
    ) -> discord.Embed:
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now(timezone.utc),
        )

        embed.set_footer(text=settings.embed_footer)
        return embed

    # ============================================================
    # EMBEDS AZULES
    # Comandos normales / respuestas generales
    # ============================================================

    def normal_embed(
        self,
        title: str,
        description: str | None = None,
    ) -> discord.Embed:
        return self.make_embed(
            title=title,
            description=description,
            color=ArgosColors.BLUE,
        )

    def command_embed(
        self,
        title: str,
        description: str | None = None,
    ) -> discord.Embed:
        return self.make_embed(
            title=title,
            description=description,
            color=ArgosColors.BLUE,
        )

    def success_embed(
        self,
        description: str,
        *,
        title: str = "Acción completada",
    ) -> discord.Embed:
        return self.make_embed(
            title=title,
            description=description,
            color=ArgosColors.BLUE,
        )

    # ============================================================
    # EMBEDS ROJOS
    # Advertencias / errores / alertas / urgencias
    # ============================================================

    def error_embed(
        self,
        description: str,
        *,
        title: str = "No se pudo completar la acción",
    ) -> discord.Embed:
        return self.make_embed(
            title=title,
            description=description,
            color=ArgosColors.RED,
        )

    def warning_embed(
        self,
        description: str,
        *,
        title: str = "Advertencia",
    ) -> discord.Embed:
        return self.make_embed(
            title=title,
            description=description,
            color=ArgosColors.RED,
        )

    def alert_embed(
        self,
        description: str,
        *,
        title: str = "Alerta",
    ) -> discord.Embed:
        return self.make_embed(
            title=title,
            description=description,
            color=ArgosColors.RED,
        )

    def urgent_embed(
        self,
        description: str,
        *,
        title: str = "Acción urgente",
    ) -> discord.Embed:
        return self.make_embed(
            title=title,
            description=description,
            color=ArgosColors.RED,
        )

    # ============================================================
    # EMBEDS NARANJOS
    # Logs / información especial / eventos administrativos
    # ============================================================

    def log_embed(
        self,
        title: str,
        description: str | None = None,
    ) -> discord.Embed:
        return self.make_embed(
            title=title,
            description=description,
            color=ArgosColors.ORANGE,
        )

    def special_info_embed(
        self,
        title: str,
        description: str | None = None,
    ) -> discord.Embed:
        return self.make_embed(
            title=title,
            description=description,
            color=ArgosColors.ORANGE,
        )

    # ============================================================
    # EMBEDS GRISES
    # Por definir / neutral
    # ============================================================

    def neutral_embed(
        self,
        title: str,
        description: str | None = None,
    ) -> discord.Embed:
        return self.make_embed(
            title=title,
            description=description,
            color=ArgosColors.GRAY,
        )

    # ============================================================
    # RESPUESTAS A INTERACCIONES
    # ============================================================

    async def respond_embed(
        self,
        interaction: discord.Interaction,
        embed: discord.Embed,
        *,
        ephemeral: bool = False,
    ) -> None:
        """
        Responde a una interacción usando embeds.

        Si la interacción ya fue respondida, usa followup.
        Esto evita errores cuando un comando tarda o ya hizo defer.
        """

        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=ephemeral)
            return

        await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

    async def deny(
        self,
        interaction: discord.Interaction,
        reason: str = "No tienes permisos para usar este comando.",
    ) -> None:
        embed = self.error_embed(
            title="Acceso denegado",
            description=reason,
        )

        await self.respond_embed(interaction, embed, ephemeral=True)
