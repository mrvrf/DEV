import discord
from discord.ext import commands, tasks
from datetime import datetime, timedelta
import asyncio

class Alert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.alert_time = "19:50"  # Specify the time in HH:MM format
        self.channel_id = 1119767862383476797  # Replace with your channel ID
        self.message = "Aguardando confere. \nUtilize **/confere** para liberar o participar."  # Specify the alert message
        self.check_time.start()

    def cog_unload(self):
        self.check_time.cancel()


    
    @tasks.loop(seconds=60)  # Check every minute
    async def check_time(self):
        user_id1 = 216766180633870338
        user1 = await self.bot.fetch_user(user_id1)
        user_id2 = 1172598336960868402
        user2 = await self.bot.fetch_user(user_id2)
        user_id3 = 942762192728629260
        user3 = await self.bot.fetch_user(user_id3)
        now = datetime.now()
        alert_time = datetime.strptime(self.alert_time, "%H:%M").time()

        # Check if the current time matches the alert time
        if now.time().hour == alert_time.hour and now.time().minute == alert_time.minute:
            channel = self.bot.get_channel(self.channel_id)
            print(f"Aguardando confere; Current time: {now.time()}, Alert time: {alert_time}")
            if channel:
                embed = discord.Embed(
                    title="Aviso de Confere",
                    description=self.message,
                    color=0x00FF00,
                    timestamp=datetime.now()
                )
                embed.set_footer(text=f"Alerta de Confere", icon_url=self.bot.user.avatar.url)
                await user1.send(embed=embed)
                await user2.send(embed=embed)
                await user3.send(embed=embed)
                await channel.send(f"<@216766180633870338> <@1172598336960868402> <@942762192728629260>")
                await channel.send(embed=embed)
                await asyncio.sleep(120)  # Wait a minute to avoid sending multiple alerts

    @check_time.before_loop
    async def before_check_time(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Alert(bot))