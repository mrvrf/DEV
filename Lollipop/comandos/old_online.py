import discord
from discord.ext import commands
from datetime import datetime

class OnlineStatus(commands.Cog):
    def __init__(self, bot: commands.Bot, role_id: int, channel_id: int):
        self.bot = bot
        self.role_id = role_id
        self.channel_id = channel_id

    @commands.Cog.listener()
    async def on_presence_update(self, before: discord.Member, after: discord.Member):
        print(f"on_presence_update triggered for {after.display_name}")
        role = discord.utils.get(after.guild.roles, id=self.role_id)
        if role:
            print(f"Role {role.name} found")
            if role in after.roles:
                print(f"User {after.display_name} has the role {role.name}")
                if before.status != after.status:
                    print(f"Status changed for {after.display_name}: {before.status} -> {after.status}")
                    channel = self.bot.get_channel(self.channel_id)
                    if channel:
                        print(f"Channel {channel.name} found")
                        permissions = channel.permissions_for(after.guild.me)
                        if permissions.send_messages:
                            print(f"Bot has permission to send messages in {channel.name}")
                            if after.status == discord.Status.online:
                                await channel.send(f"{after.display_name} está online")
                                print(f"Sent online message for {after.display_name}")
                            elif after.status == discord.Status.offline:
                                await channel.send(f"{after.display_name} está offline")
                                print(f"Sent offline message for {after.display_name}")
                        else:
                            print("Bot does not have permission to send messages in the channel")
                    else:
                        print("Channel not found")
            else:
                print(f"User {after.display_name} does not have the role {role.name}")
        else:
            print("Role not found")

async def setup(bot: commands.Bot):
    role_id = 929480758328975381  # Replace with your role ID
    channel_id = 1318401148151009391  # Replace with your channel ID
    await bot.add_cog(OnlineStatus(bot, role_id, channel_id))