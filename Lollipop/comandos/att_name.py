import discord
from discord.ext import commands, tasks
import sqlite3
from datetime import datetime

class AttName(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_id = 1395196503261446146  # Replace with your role ID
        self.update_names.start()

    def cog_unload(self):
        self.update_names.cancel()

    @tasks.loop(hours=1)
    async def update_names(self):
        try:
            guild = self.bot.get_guild(929343217915297812)  # Replace with your guild ID
            if not guild:
                print(f"{datetime.now()}: Guild not found")
                return

            role = guild.get_role(self.role_id)
            if not role:
                print(f"{datetime.now()}: Role not found")
                return

            with sqlite3.connect('profiles.db') as conn:
                c = conn.cursor()
                
                for member in role.members:
                    # Check if member has profile
                    c.execute('SELECT family_name FROM profiles WHERE user_id = ?', 
                            (member.id,))
                    data = c.fetchone()
                    
                    if data:
                        new_nick = f"🍭 {data[0]}"
                        try:
                            await member.edit(nick=new_nick)
                            print(f"{datetime.now()}: Updated {member.name} to {new_nick}")
                        except discord.Forbidden:
                            print(f"{datetime.now()}: Cannot change nickname for {member.name}")
                        except Exception as e:
                            print(f"{datetime.now()}: Error changing nickname for {member.name}: {e}")

        except Exception as e:
            print(f"{datetime.now()}: Error in update_names: {e}")

    @update_names.before_loop
    async def before_update_names(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(AttName(bot))