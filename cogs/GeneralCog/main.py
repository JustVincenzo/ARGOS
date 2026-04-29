from __future__ import annotations

from datetime import datetime, timezone

import discord
from discord import app_commands

from base_cog import BaseCog


class GeneralCog(BaseCog):
    """
    ARGOS General

    Comandos básicos del bot:
    - /ping
    - /info
    - /servidor
    - /usuario
    - /avatar
    - /ayuda
    """

    module_name = "General"

    @app_commands.command(
        name="ping",
        description="Muestra la latencia actual de ARGOS.",
    )
    async def ping(self, interaction: discord.Interaction) -> None:
        latency_ms = round(self.bot.latency * 1000)

        embed = self.command_embed(
            title="Latencia de ARGOS",
            description=f"ARGOS está operativo.\n\n**Latencia:** `{latency_ms} ms`",
        )

        await self.respond_embed(interaction, embed)

    @app_commands.command(
        name="info",
        description="Muestra información general sobre ARGOS.",
    )
    async def info(self, interaction: discord.Interaction) -> None:
        bot_user = self.bot.user

        if bot_user is None:
            embed = self.error_embed(
                title="Error interno",
                description="No se pudo obtener la información del bot.",
            )
            await self.respond_embed(interaction, embed, ephemeral=True)
            return

        embed = self.command_embed(
            title="ARGOS",
            description=(
                "ARGOS es un sistema modular para Discord diseñado para servidores "
                "hispanohablantes. Su objetivo es apoyar al staff con herramientas de "
                "moderación, registros, tickets, seguridad, utilidades e inteligencia "
                "artificial controlada."
            ),
        )

        embed.add_field(
            name="Identidad",
            value="Este bot fue codificado con Python usando el framework ´discord.py´.
            Fue codificado por <@1078714238417248276>",
            inline=False,
        )

        embed.add_field(
            name="Estado",
            value="Operativo",
            inline=True,
        )

        embed.add_field(
            name="Latencia",
            value=f"`{round(self.bot.latency * 1000)} ms`",
            inline=True,
        )

        embed.add_field(
            name="Servidores",
            value=f"`{len(self.bot.guilds)}`",
            inline=True,
        )

        embed.set_thumbnail(url=bot_user.display_avatar.url)

        await self.respond_embed(interaction, embed)

    @app_commands.command(
        name="servidor",
        description="Muestra información del servidor actual.",
    )
    @app_commands.guild_only()
    async def servidor(self, interaction: discord.Interaction) -> None:
        guild = interaction.guild

        if guild is None:
            embed = self.error_embed(
                title="Comando no disponible",
                description="Este comando solo puede usarse dentro de un servidor.",
            )
            await self.respond_embed(interaction, embed, ephemeral=True)
            return

        owner_text = "No disponible"

        if guild.owner is not None:
            owner_text = guild.owner.mention
        elif guild.owner_id is not None:
            owner_text = f"`{guild.owner_id}`"

        created_at = int(guild.created_at.replace(tzinfo=timezone.utc).timestamp())

        embed = self.command_embed(
            title=f"Información de {guild.name}",
            description="Datos generales del servidor.",
        )

        embed.add_field(
            name="ID del servidor",
            value=f"`{guild.id}`",
            inline=False,
        )

        embed.add_field(
            name="Propietario",
            value=owner_text,
            inline=True,
        )

        embed.add_field(
            name="Miembros",
            value=f"`{guild.member_count or 0}`",
            inline=True,
        )

        embed.add_field(
            name="Canales",
            value=f"`{len(guild.channels)}`",
            inline=True,
        )

        embed.add_field(
            name="Roles",
            value=f"`{len(guild.roles)}`",
            inline=True,
        )

        embed.add_field(
            name="Emojis",
            value=f"`{len(guild.emojis)}`",
            inline=True,
        )

        embed.add_field(
            name="Creado",
            value=f"<t:{created_at}:D>\n<t:{created_at}:R>",
            inline=True,
        )

        if guild.icon is not None:
            embed.set_thumbnail(url=guild.icon.url)

        await self.respond_embed(interaction, embed)

    @app_commands.command(
        name="usuario",
        description="Muestra información de un usuario del servidor.",
    )
    @app_commands.describe(
        miembro="Usuario que quieres revisar. Si no eliges uno, se mostrará tu información.",
    )
    @app_commands.guild_only()
    async def usuario(
        self,
        interaction: discord.Interaction,
        miembro: discord.Member | None = None,
    ) -> None:
        target = miembro or interaction.user

        if not isinstance(target, discord.Member):
            embed = self.error_embed(
                title="Usuario no disponible",
                description="No se pudo obtener la información del miembro.",
            )
            await self.respond_embed(interaction, embed, ephemeral=True)
            return

        created_at = int(target.created_at.replace(tzinfo=timezone.utc).timestamp())

        joined_text = "No disponible"
        if target.joined_at is not None:
            joined_at = int(target.joined_at.replace(tzinfo=timezone.utc).timestamp())
            joined_text = f"<t:{joined_at}:D>\n<t:{joined_at}:R>"

        roles = [
            role.mention
            for role in target.roles
            if role.name != "@everyone"
        ]

        roles_text = ", ".join(roles[-10:]) if roles else "Sin roles visibles."

        if len(roles) > 10:
            roles_text += f"\nY `{len(roles) - 10}` roles más."

        embed = self.command_embed(
            title=f"Información de {target.display_name}",
            description=f"Datos generales de {target.mention}.",
        )

        embed.add_field(
            name="ID",
            value=f"`{target.id}`",
            inline=False,
        )

        embed.add_field(
            name="Cuenta creada",
            value=f"<t:{created_at}:D>\n<t:{created_at}:R>",
            inline=True,
        )

        embed.add_field(
            name="Se unió al servidor",
            value=joined_text,
            inline=True,
        )

        embed.add_field(
            name="Bot",
            value="Sí" if target.bot else "No",
            inline=True,
        )

        embed.add_field(
            name="Rol superior",
            value=target.top_role.mention if target.top_role else "No disponible",
            inline=True,
        )

        embed.add_field(
            name="Roles",
            value=roles_text,
            inline=False,
        )

        embed.set_thumbnail(url=target.display_avatar.url)

        await self.respond_embed(interaction, embed)

    @app_commands.command(
        name="avatar",
        description="Muestra el avatar de un usuario.",
    )
    @app_commands.describe(
        usuario="Usuario cuyo avatar quieres ver. Si no eliges uno, se mostrará el tuyo.",
    )
    async def avatar(
        self,
        interaction: discord.Interaction,
        usuario: discord.User | None = None,
    ) -> None:
        target = usuario or interaction.user

        avatar_url = target.display_avatar.url

        embed = self.command_embed(
            title=f"Avatar de {target.display_name}",
            description=f"[Abrir imagen]({avatar_url})",
        )

        embed.set_image(url=avatar_url)

        await self.respond_embed(interaction, embed)

    @app_commands.command(
        name="ayuda",
        description="Muestra los comandos principales de ARGOS.",
    )
    async def ayuda(self, interaction: discord.Interaction) -> None:
        embed = self.command_embed(
            title="Ayuda de ARGOS",
            description="Comandos generales disponibles actualmente.",
        )

        embed.add_field(
            name="General",
            value=(
                "`/ping` — Muestra la latencia del bot.\n"
                "`/info` — Muestra información de ARGOS.\n"
                "`/servidor` — Muestra información del servidor.\n"
                "`/usuario` — Muestra información de un usuario.\n"
                "`/avatar` — Muestra el avatar de un usuario.\n"
                "`/ayuda` — Muestra esta ayuda."
            ),
            inline=False,
        )

        embed.add_field(
            name="Módulos futuros",
            value=(
                "`ARGOS Guardia` — Moderación.\n"
                "`ARGOS Vigía` — Logs.\n"
                "`ARGOS Mesa` — Tickets.\n"
                "`ARGOS Oráculo` — IA controlada.\n"
                "`ARGOS Léxico` — Diccionario y lenguaje."
            ),
            inline=False,
        )

        await self.respond_embed(interaction, embed)


async def setup(bot) -> None:
    await bot.add_cog(GeneralCog(bot))
