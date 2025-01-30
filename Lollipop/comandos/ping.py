import discord
from discord.ext import commands
from discord import app_commands

class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @app_commands.checks.has_permissions(administrator=True)
    async def ping(self, ctx):
        await ctx.send('Bot online')

async def setup(bot):
    await bot.add_cog(Ping(bot))
