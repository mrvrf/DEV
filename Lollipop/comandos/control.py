import discord
from discord.ext import commands
from discord import app_commands
from comandos.db import update_user_response
import aiosqlite
from typing import Literal
from datetime import datetime

DATABASE_GVG = 'gvg.db'

class ControlCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.control_group = app_commands.Group(name="control", description="Main control command")

        @self.control_group.command(name="delete", description="Deleta alguma presença criada")
        @app_commands.guild_only()
        @app_commands.checks.has_role(1325386396214628454)
        async def delete_presenca(interaction: discord.Interaction, column: str):
            log_embed = discord.Embed(
            title="**Comando Executado**",
            description=f"**Comando:** */control delete {column}*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
            color=0xFFFFFF
            )
            log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

            log_channel = interaction.guild.get_channel(1318401148151009391)
            await log_channel.send(embed=log_embed)

            columns = await self.get_columns()
            if column not in columns:
                await interaction.response.send_message(f"Column {column} does not exist.", ephemeral=True)
                return

            async with aiosqlite.connect(DATABASE_GVG) as db:
                try:
                    await db.execute(f'ALTER TABLE gvg DROP COLUMN "{column}"')
                    await db.commit()
                    await interaction.response.send_message(f"Presença {column} deletada.", ephemeral=True)
                except Exception as e:
                    await interaction.response.send_message(f"Error deleting column: {e}", ephemeral=True)

        self.delete_presenca = delete_presenca


        @self.control_group.command(name="set", description="Modifica a presença de um membro")
        @app_commands.guild_only()
        @app_commands.checks.has_role(1325386396214628454)
        async def set_presenca(interaction: discord.Interaction, user: discord.Member, status: Literal["SIM", "NAO"], column: str):
            log_embed = discord.Embed(
            title="**Comando Executado**",
            description=f"**Comando:** */control set ({status}) {user}*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
            color=0xFFFFFF
            )
            log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

            # Envia o log para um canal específico
            log_channel = interaction.guild.get_channel(1318401148151009391)
            await log_channel.send(embed=log_embed)
            columns = await self.get_columns()
            if column not in columns:
                await interaction.response.send_message(f"Column {column} does not exist.", ephemeral=True)
                return

            try:
                await update_user_response(str(user.id), column, status)
                await interaction.response.send_message(f"Presença do {user.display_name} modificada para {status} na presença {column}.", ephemeral=True)
            except Exception as e:
                await interaction.response.send_message(f"Error setting presenca: {e}", ephemeral=True)

        self.set_presenca = set_presenca

    async def get_columns(self):
        async with aiosqlite.connect(DATABASE_GVG) as db:
            async with db.execute("PRAGMA table_info(gvg)") as cursor:
                columns = [column[1] for column in await cursor.fetchall()]
        return columns
    

        

async def setup(bot: commands.Bot):
    control_command = ControlCommand(bot)
    bot.tree.add_command(control_command.control_group)
    await bot.add_cog(control_command)