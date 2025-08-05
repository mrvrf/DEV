import discord
from discord.ext import commands
from discord import app_commands

class Self(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="me", description="alguma coisa")
    @app_commands.guild_only()
    @app_commands.checks.has_role(1325386396214628454)
    async def me(self, interaction: discord.Interaction, message: str):
        await interaction.channel.send(message)

async def setup(bot):
    await bot.add_cog(Self(bot))