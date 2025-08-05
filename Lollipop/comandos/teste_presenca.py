import discord
from discord.ext import commands
from discord import app_commands
import aiosqlite
import re

DATABASE_GVG = 'gvg.db'

class TestePresenca(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def create_column(self, column: str):
        async with aiosqlite.connect(DATABASE_GVG) as db:
            await db.execute(f'ALTER TABLE gvg ADD COLUMN "{column}" TEXT')
            await db.commit()

    async def update_user_presence(self, user_id: str, column: str):
        async with aiosqlite.connect(DATABASE_GVG) as db:
            await db.execute(f'UPDATE gvg SET "{column}" = "SIM" WHERE "UserID" = ?', (user_id,))
            await db.commit()

    @app_commands.command(name="txt", description="Upload a .txt file to update presence")
    @app_commands.guild_only()
    @app_commands.checks.has_role(1325386396214628454)
    async def txt(self, interaction: discord.Interaction, column: str, file: discord.Attachment):
        try:
            if not file.filename.endswith('.txt'):
                await interaction.response.send_message("Please upload a valid .txt file.", ephemeral=True)
                return

            # Create the new column
            await self.create_column(column)

            # Read the content of the file
            content = await file.read()
            content = content.decode('utf-8')

            # Extract usernames from the content
            usernames = re.findall(r'\((.*?)\)', content)

            # Update presence for each username
            updated_users = []
            for username in usernames:
                member = discord.utils.get(interaction.guild.members, name=username)
                if member:
                    await self.update_user_presence(str(member.id), column)
                    updated_users.append(username)

            # Send response
            if updated_users:
                await interaction.response.send_message(f"Presence updated for users in column {column}: {', '.join(updated_users)}", ephemeral=True)
            else:
                await interaction.response.send_message(f"No valid usernames found in the file.", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(TestePresenca(bot))