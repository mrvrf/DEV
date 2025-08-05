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

            if self.user_message_count == 15:
                await message.channel.send(f"<@185478267220787200> https://tenor.com/view/calma-papagaio-paiz%C3%A3o-gif-2999973167135261920")
                self.user_message_count = 0

class Hammysz(commands.Cog):
    def __init__(self, bot: commands.Bot, specified_user_id2: int):
        self.bot = bot
        self.specified_user_id2 = specified_user_id2
        self.user_message_count = 0

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.author.id == self.specified_user_id2:
            self.user_message_count += 1

            if self.user_message_count == 30:
                await message.channel.send(f"<@1254473982711828584> https://cdn.discordapp.com/attachments/959257911274659961/1328826492116799488/meme_4.gif?ex=679d359c&is=679be41c&hm=a090b653af1a27a97761ce3b2e1621ac188be03280f9e1f3ac6e186f4dc2f518&")
                self.user_message_count = 0

class Kormel(commands.Cog):
    def __init__(self, bot: commands.Bot, specified_user_id3: int):
        self.bot = bot
        self.specified_user_id3 = specified_user_id3
        self.user_message_count = 0

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return

        if message.author.id == self.specified_user_id3:
            self.user_message_count += 1

            if self.user_message_count == 30:
                await message.channel.send(f"<@942762192728629260> https://cdn.discordapp.com/attachments/959257911274659961/1328826492116799488/meme_4.gif?ex=679d359c&is=679be41c&hm=a090b653af1a27a97761ce3b2e1621ac188be03280f9e1f3ac6e186f4dc2f518&")
                self.user_message_count = 0

async def setup(bot: commands.Bot):
    specified_user_id = 185478267220787200
    specified_user_id2 = 1254473982711828584
    specified_user_id3 = 942762192728629260
    
    await bot.add_cog(Alone(bot, specified_user_id))
    #await bot.add_cog(Hammysz(bot, specified_user_id2))
    #await bot.add_cog(Kormel(bot, specified_user_id3))