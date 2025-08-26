import discord
from discord.ext import commands
from datetime import datetime

class BotLog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.log_channel_id = 929480761885741117  # ID do canal
        self.embed_color_rosa = 0xFF10D4  # Cor default do embed
        self.embed_color_verde = 0x4dff00 # Cor verde embed
        self.embed_color_vermelho = 0xcc0000 # Cor vermelho embed
        self.embed_color_preto = 0x000000 # Cor preto embed

    @commands.Cog.listener()
    async def on_member_join(self, member):

        # Define colors
        verde = self.embed_color_verde

        try:
            # Get the log channel
            log_channel = self.bot.get_channel(self.log_channel_id)
            if not log_channel:
                print(f"Log channel not found: {self.log_channel_id}")
                return

            # Create embed
            embed = discord.Embed(
                title="Usuário entrou no servidor",
                description=f"{member.mention} entrou no servidor!",
                color=verde,
                timestamp=datetime.now()
            )
            
            # Add member info
            embed.add_field(name="Nome", value=member.name, inline=True)
            embed.add_field(name="ID", value=member.id, inline=True)
            embed.add_field(name="Conta Criada", value=member.created_at.strftime("%d/%m/%Y"), inline=False)
            
            # Set thumbnail to member avatar
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            
            # Send embed
            await log_channel.send(embed=embed)
            
        except Exception as e:
            print(f"Error in on_member_join: {e}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        # Define colors
        vermelho = self.embed_color_vermelho

        try:
            # Get the log channel
            log_channel = self.bot.get_channel(self.log_channel_id)
            if not log_channel:
                print(f"Log channel not found: {self.log_channel_id}")
                return

            # Create embed
            embed = discord.Embed(
                title="Usuário saiu do servidor",
                description=f"{member.mention} saiu do servidor!",
                color=vermelho,
                timestamp=datetime.now()
            )
            
            # Add member info
            embed.add_field(name="Nome", value=member.name, inline=True)
            embed.add_field(name="ID", value=member.id, inline=True)
            embed.add_field(name="Entrou em", value=member.joined_at.strftime("%d/%m/%Y"), inline=False)
            
            # Set thumbnail to member avatar
            embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
            
            # Send embed
            await log_channel.send(embed=embed)
            
        except Exception as e:
            print(f"Error in on_member_left: {e}")

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        # Define colors
        preto = self.embed_color_preto

        try:
            # Get the log channel
            log_channel = self.bot.get_channel(self.log_channel_id)
            if not log_channel:
                print(f"Log channel not found: {self.log_channel_id}")
                return

            # Create embed
            embed = discord.Embed(
                title="Usuário banido do servidor",
                description=f"{user.mention} foi banido do servidor!",
                color=preto,
                timestamp=datetime.now()
            )
            
            # Add user info
            embed.add_field(name="Nome", value=user.name, inline=True)
            embed.add_field(name="ID", value=user.id, inline=True)
            
            # Set thumbnail to user avatar
            embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
            
            # Send embed
            await log_channel.send(embed=embed)
            
        except Exception as e:
            print(f"Error in on_member_ban: {e}")

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        try:
            log_channel = self.bot.get_channel(self.log_channel_id)
            if not log_channel:
                return

            # Check for role changes
            added_roles = [role for role in after.roles if role not in before.roles]
            removed_roles = [role for role in before.roles if role not in after.roles]

            rosa = self.embed_color_rosa

            # Handle added roles
            for role in added_roles:
                embed = discord.Embed(
                    title="",
                    description=f"Cargo {role.mention} **adicionado** para {after.mention}",
                    color=rosa,
                    timestamp=datetime.now()
                )
                embed.set_author(name="Cargo Adicionado", icon_url=after.avatar.url if after.avatar else after.default_avatar.url)
                embed.set_footer(text=f"ID: {after.id} - {after.name}")
                await log_channel.send(embed=embed)

            # Handle removed roles
            for role in removed_roles:
                embed = discord.Embed(
                    title="",
                    description=f"Cargo {role.mention} **removido** de {after.mention}",
                    color=rosa,
                    timestamp=datetime.now()
                )
                embed.set_author(name="Cargo Removido", icon_url=after.avatar.url if after.avatar else after.default_avatar.url)
                embed.set_footer(text=f"ID: {after.id} - {after.name}")
                await log_channel.send(embed=embed)

        except Exception as e:
            print(f"Error in on_member_update: {e}")

async def setup(bot):
    await bot.add_cog(BotLog(bot))