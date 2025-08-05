import discord
from discord.ext import commands
import asyncio

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="_", intents=intents)

    async def on_ready(self):
        print(f"Logged in as {self.user} and ready!")

# Replace 'YOUR_TOKEN_HERE' with your bot's token
bot = MyBot()

bot.run("NDQwNzUzODM1MTQxNzU4OTg2.G_qyFK.AcWQvm9ADDxnqWD_QlbfiqpEhru60sqZgsm_mY")