import discord
from discord.ext import commands
from datetime import datetime

class PresenceStatus(commands.Cog):
    def __init__(self, bot: commands.Bot, role_al: int, role_go: int, role_mn: int, channel_id: int):
        self.bot = bot
        self.role_al = role_al
        self.role_go = role_go
        self.role_mn = role_mn
        self.channel_id = channel_id

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        roles = {
            "A": self.role_al,
            "G": self.role_go,
            "M": self.role_mn
        }
        for prefix, role_id in roles.items():
            role = discord.utils.get(after.guild.roles, id=role_id)
            if role and role in after.roles and before.status != after.status:
                channel = self.bot.get_channel(self.channel_id)
                if channel and channel.permissions_for(after.guild.me).send_messages:
                    status_message = {
                        discord.Status.online: "está online (:green_circle:)",
                        discord.Status.idle: "está ausente (:yellow_circle:)",
                        discord.Status.dnd: "está online (:red_circle:)",
                        discord.Status.offline: "está offline"
                    }.get(after.status, "mudou de status")
                    await channel.send(f"({prefix}) **{after.display_name} {status_message}** - {datetime.now().strftime('%d/%m/%Y | %H:%M')}")

async def setup(bot: commands.Bot):
    channel_id = 1335865355553345596  # Replace with your channel ID
    role_al = 929344073221935104  # Replace with your role ID for allyance
    role_go = 935733958266716200  # Replace with your role ID for grand_order
    role_mn = 1206381250064158740  # Replace with your role ID for manifest
    await bot.add_cog(PresenceStatus(bot, role_al, role_go, role_mn, channel_id))