import discord
from discord.ext import commands, tasks
from datetime import datetime
import asyncio

class Alert(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.alert_time = "19:50"  # Specify the time in HH:MM format
        self.labs = "22:00"
        self.channel_id = 1119767862383476797  # Replace with your channel ID
        self.message = "Aguardando confere. \nUtilize **/confere** para liberar o participar.\nhttps://discord.com/channels/929343217915297812/1119767862383476797"  # Specify the alert message
        self.labs_message = "**MANDA LABS AI PAIZAO** \nLABS DO **CAPADO** https://discord.com/channels/929343217915297812/1167607962542547054\nLABS DO **DESCAPADO** https://discord.com/channels/929343217915297812/1330036510493507584"
        self.check_time.start()

    def cog_unload(self):
        self.check_time.cancel()


    
    @tasks.loop(minutes=1)  # Check every minute
    async def check_time(self):
        user_id1 = 216766180633870338 #Ninon
        user1 = await self.bot.fetch_user(user_id1)
        user_id2 = 1172598336960868402 #Mitsuri
        user2 = await self.bot.fetch_user(user_id2)
        user_id3 = 942762192728629260 #Kormel
        user3 = await self.bot.fetch_user(user_id3)
        user_id4 = 253711374235074560 #Lari
        user4 = await self.bot.fetch_user(user_id4)
        user_id5 = 852612478877433897 #Soaria
        user5 = await self.bot.fetch_user(user_id5)
        user_id6 = 285498546273386498 #Toushiro
        user6 = await self.bot.fetch_user(user_id6)
        meriove = 268471873073840128
        user_id7 = 303558557968629763 #Rabbit
        user7 = await self.bot.fetch_user(user_id7)
        user_id8 = 911832664431001680 #Inori
        user8 = await self.bot.fetch_user(user_id8)
        user_id9 = 236655197542154243 #Angellus
        user9 = await self.bot.fetch_user(user_id9)
        user_meriove = await self.bot.fetch_user(meriove)
        now = datetime.now()
        alert_time = datetime.strptime(self.alert_time, "%H:%M").time()
        labs = datetime.strptime(self.labs, "%H:%M").time()

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
                embed.set_footer(text=f"Alerta de Confere (19:50)", icon_url=self.bot.user.avatar.url)
                #await user1.send(embed=embed)
                #await user2.send(embed=embed)
                await user3.send(embed=embed)
                await user4.send(embed=embed)
                await user7.send(embed=embed)
                await user8.send(embed=embed)
                #await channel.send(f"<@216766180633870338> <@1172598336960868402> <@942762192728629260> <@253711374235074560>")
                #await channel.send(embed=embed)
                await asyncio.sleep(120)  # Wait a minute to avoid sending multiple alerts

        if now.time().hour == labs.hour and now.time().minute == labs.minute:
            print(f"Aguardando labs; Current time: {now.time()}, Alert time: {labs}")
            labs_embed = discord.Embed(
                title="Aviso de Labs",
                description=self.labs_message,
                color=0x00FF00,
                timestamp=datetime.now()
            )
            labs_embed.set_footer(text=f"Alerta de Labs (22:00)", icon_url=self.bot.user.avatar.url)
            await user3.send(embed=labs_embed)
            await user4.send(embed=labs_embed)
            await user5.send(embed=labs_embed)
            await user6.send(embed=labs_embed)
            await user7.send(embed=labs_embed)
            await user8.send(embed=labs_embed)
            await user9.send(embed=labs_embed)

    @check_time.before_loop
    async def before_check_time(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Alert(bot))