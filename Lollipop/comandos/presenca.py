import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Modal, TextInput
from comandos.db import update_gvg_presence, get_user_profile, update_user_response
from datetime import datetime
import asyncio
import aiosqlite

DATABASE_GVG = 'gvg.db'

class PinModal(Modal):
    def __init__(self, user_id: str, column_name: str, pin: str):
        super().__init__(title="Enter PIN")
        self.user_id = user_id
        self.column_name = column_name
        self.pin = pin
        self.add_item(TextInput(label="PIN", placeholder="Enter the PIN"))

    async def on_submit(self, interaction: discord.Interaction):
        entered_pin = self.children[0].value
        response = "SIM" if entered_pin == self.pin else "NAO"
        await update_user_response(self.user_id, self.column_name, response)
        await interaction.response.send_message("Thank you for your response!", ephemeral=True)

class PresencaCommand(commands.Cog):
    def __init__(self, bot: commands.Bot, role_id: int, guild_id: int):
        self.bot = bot
        self.role_id = role_id
        self.guild_id = guild_id

    async def get_columns(self):
        async with aiosqlite.connect(DATABASE_GVG) as db:
            async with db.execute("PRAGMA table_info(gvg)") as cursor:
                columns = [column[1] for column in await cursor.fetchall() if column[1] != "UserID"]
        return columns

    async def get_user_sim_counts(self):
        columns = await self.get_columns()
        # Enclose each column name in double quotes to handle spaces
        quoted_columns = [f'"{column}"' for column in columns]
        user_sim_counts = {}
        async with aiosqlite.connect(DATABASE_GVG) as db:
            query = f'SELECT UserID, {", ".join(quoted_columns)} FROM gvg'
            async with db.execute(query) as cursor:
                async for row in cursor:
                    user_id = row[0]
                    sim_count = sum(1 for value in row[1:] if value == "SIM")
                    user_sim_counts[user_id] = sim_count
        return user_sim_counts

    async def get_users_with_sim(self, column: str):
        users_with_sim = []
        async with aiosqlite.connect(DATABASE_GVG) as db:
            async with db.execute(f'SELECT "UserID" FROM gvg WHERE "{column}" = "SIM"') as cursor:
                async for row in cursor:
                    users_with_sim.append(row[0])
        return users_with_sim

    @app_commands.command(name="presenca", description="Envia presença de gvg")
    @app_commands.guild_only()
    @app_commands.checks.has_role(1325386396214628454)
    async def presenca(self, interaction: discord.Interaction, canal_voz: discord.VoiceChannel, nome: str, pin: str):
        try:
            await interaction.response.defer(ephemeral=True)
            log_embed = discord.Embed(
                title="**Comando Executado**",
                description=f"**Comando:** */presenca*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
                color=0xFFFFFF
            )
            log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

            log_channel = interaction.guild.get_channel(1318401148151009391)
            war_room = interaction.guild.get_channel(1126288833655349308)
            await log_channel.send(embed=log_embed)    
            await war_room.send(f"Presença de GVG atualizada por {interaction.user.mention} para {nome}.")
            
            guild = self.bot.get_guild(self.guild_id)
            if guild:
                role = guild.get_role(self.role_id)
                if role:
                    role_members = role.members
                    voice_channel_members = canal_voz.members
                    print(f"Calling update_gvg_presence with column name: {nome}")
                    await update_gvg_presence(role_members, voice_channel_members, nome)
                    
                    for member in voice_channel_members:
                        try:
                            await member.send("Please enter the PIN you received:", view=PinModal(str(member.id), nome, pin))
                        except Exception as e:
                            print(f"Error sending PIN to {member.display_name}: {e}")

                    await interaction.followup.send("Presença atualizada com sucesso!", ephemeral=True)
                else:
                    await interaction.followup.send("Erro ao atualizar a presença. Cargo não encontrado.", ephemeral=True)
            else:
                await interaction.followup.send("Erro ao atualizar a presença. Servidor não encontrado.", ephemeral=True)
        except Exception as e:
            print(f"Erro ao atualizar a presença: {e}")
            await interaction.followup.send("Erro ao atualizar a presença.", ephemeral=True)

    @app_commands.command(name="perfil", description="Mostra o perfil de um usuário")
    @app_commands.guild_only()
    @app_commands.checks.has_role(1326000068448489502)
    async def perfil(self, interaction: discord.Interaction, user: discord.Member):
        try:
            log_embed = discord.Embed(
                title="**Comando Executado**",
                description=f"**Comando:** */perfil*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
                color=0xFFFFFF
            )
            log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

            log_channel = interaction.guild.get_channel(1318401148151009391)
            await log_channel.send(embed=log_embed)
            user_sim_counts = await self.get_user_sim_counts()

            profile = await get_user_profile(str(user.id))
            if profile:
                embed = discord.Embed(title=f"Presença - {user.display_name}", color=0xB4A7D6)
                embed.set_thumbnail(url=user.avatar.url)
                embed.set_footer(text=f"Total presenças: {user_sim_counts.get(str(user.id), 0)}")
                for key, value in profile.items():
                    if key != "UserID":
                        embed.add_field(name=key, value=value if value else "N/A", inline=False)
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                await interaction.response.send_message("Perfil não encontrado.", ephemeral=True)
        except Exception as e:
            print(f"Error in /perfil command: {e}")
            await interaction.response.send_message("An error occurred while processing the command.", ephemeral=True)

    @app_commands.command(name="pre", description="Checa seu perfil de presença em gvg")
    @app_commands.guild_only()
    @app_commands.checks.has_role(929480758328975381)
    async def pre(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            log_embed = discord.Embed(
                title="**Comando Executado**",
                description=f"**Comando:** */pre*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
                color=0xFFFFFF
            )
            log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

            log_channel = interaction.guild.get_channel(1318401148151009391)
            await log_channel.send(embed=log_embed)
            user_sim_counts = await self.get_user_sim_counts()
            
            profile = await get_user_profile(str(interaction.user.id))
            if profile:
                embed = discord.Embed(title=f"{interaction.user.display_name}", color=0xB4A7D6)
                embed.set_thumbnail(url=interaction.user.avatar.url)
                embed.set_footer(text=f"Total presenças: {user_sim_counts.get(str(interaction.user.id), 0)}")
                for key, value in profile.items():
                    if key != "UserID":
                        embed.add_field(name=key, value=value if value else "N/A", inline=False)
                await interaction.followup.send("Perfil encontrado. Verificando a sua presença...", ephemeral=True)
                await asyncio.sleep(3)
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                await interaction.followup.send("Perfil não encontrado.", ephemeral=True)
        except Exception as e:
            print(f"Error in /pre command: {e}")
            await interaction.followup.send("An error occurred while processing the command.", ephemeral=True)

    @app_commands.command(name="total", description="Lista dos maiores presentes nas gvgs")
    @app_commands.guild_only()
    @app_commands.checks.has_role(1326000068448489502)
    async def total(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            log_embed = discord.Embed(
                title="**Comando Executado**",
                description=f"**Comando:** */total*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
                color=0xFFFFFF
            )
            log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

            log_channel = interaction.guild.get_channel(1318401148151009391)
            await log_channel.send(embed=log_embed)

            user_sim_counts = await self.get_user_sim_counts()
            sorted_users = sorted(user_sim_counts.items(), key=lambda x: x[1], reverse=True)

            embeds = []
            description = ""
            for user_id, sim_count in sorted_users:
                member = interaction.guild.get_member(int(user_id))
                if member:
                    line = f"{member.display_name} - **{sim_count}** presenças\n"
                    if len(description) + len(line) > 4000:
                        embed = discord.Embed(title="Total de Presenças", description=description, color=0xB4A7D6)
                        embeds.append(embed)
                        description = ""
                    description += line
            if description:
                embed = discord.Embed(title="Total de Presenças", description=description, color=0xB4A7D6)
                embeds.append(embed)

            for embed in embeds:
                await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"Error in /total command: {e}")
            await interaction.followup.send("An error occurred while processing the command.", ephemeral=True)

    @app_commands.command(name="totalgvg", description="Lista a presença de quem estava em determinada GvG")
    @app_commands.guild_only()
    @app_commands.checks.has_role(1325386396214628454)
    async def totalgvg(self, interaction: discord.Interaction, column: str):
        try:
            await interaction.response.defer(ephemeral=True)
            log_embed = discord.Embed(
                title="**Comando Executado**",
                description=f"**Comando:** */totalgvg {column}*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
                color=0xFFFFFF
            )
            log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

            log_channel = interaction.guild.get_channel(1318401148151009391)
            await log_channel.send(embed=log_embed)

            users_with_sim = await self.get_users_with_sim(column)
            if not users_with_sim:
                await interaction.followup.send(f"No users found with SIM in column {column}.", ephemeral=True)
                return

            description = ""
            for user_id in users_with_sim:
                member = interaction.guild.get_member(int(user_id))
                display_name = member.display_name if member else "Unknown User"
                line = f"{display_name}\n"
                if len(description) + len(line) > 4000:
                    embed = discord.Embed(title=f"Membros na {column}", description=description, color=0xB4A7D6)
                    await interaction.followup.send(embed=embed, ephemeral=True)
                    description = ""
                description += line
            if description:
                embed = discord.Embed(title=f"Membros na {column}", description=description, color=0xB4A7D6)
                await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            print(f"Error in /totalgvg command: {e}")
            await interaction.followup.send("An error occurred while processing the command.", ephemeral=True)

async def setup(bot: commands.Bot):
    role_id = 929480758328975381  # Replace with your role ID
    guild_id = 929343217915297812  # Replace with your guild ID
    await bot.add_cog(PresencaCommand(bot, role_id, guild_id))