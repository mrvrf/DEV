import discord
from discord.ext import commands

class Alone(commands.Cog):
    def __init__(self, bot: commands.Bot, specified_user_id: int):
        self.bot = bot
        self.specified_user_id = specified_user_id
        self.user_message_count = 0

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.author.id == self.specified_user_id:
            self.user_message_count += 1

            if self.user_message_count == 30:
                await message.channel.send(f"<@185478267220787200> https://tenor.com/view/calma-papagaio-paiz%C3%A3o-gif-2999973167135261920")
                self.user_message_count = 0

async def setup(bot: commands.Bot):
    specified_user_id = 185478267220787200  # Replace with the actual user ID
    await bot.add_cog(Alone(bot, specified_user_id))