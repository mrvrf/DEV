import discord
from discord.ext import commands
from discord import app_commands
import asyncio

class Limpa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='limparole', description='Remove o cargo de todos os membros que tem ele')
    @app_commands.guild_only()
    @app_commands.checks.has_role(942666939686334524)
    @app_commands.describe(role='O cargo')
    async def limparole(self, interaction: discord.Interaction, role: discord.Role):

        await interaction.response.defer(ephemeral=True)
        if interaction.guild is None:
            await interaction.response.send_message("Este comando não pode ser usado em mensagens privadas.", ephemeral=True)
            return

        members_with_role = [member for member in interaction.guild.members if role in member.roles]

        for member in members_with_role:
            try:
                await member.remove_roles(role)
                print(f"Cargo {role.name} removido de {member.display_name}")
                await asyncio.sleep(2)
            except discord.Forbidden:
                print(f"Falha ao remover {role.name} do {member.display_name}")

        await interaction.response.send_message(f"Cargo {role.name} de {len(members_with_role)} membros.", ephemeral=True)

    @limparole.error
    async def limparole_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message("Você não tem permissão para usar este comando. Adicione o cargo <@&942666939686334524> para utilizar este comando.", ephemeral=True)
        else:
            print(f'Error in teste command: {error}')


    @app_commands.command(name='addrole', description='Adiciona um cargo a todos que estão nesse cargo')
    @app_commands.guild_only()
    @app_commands.checks.has_role(942666939686334524)
    @app_commands.describe(addcargo='O cargo a ser adicionado', cargo='O cargo selecionado')
    async def addrole(self, interaction: discord.Interaction, addcargo: discord.Role, cargo: discord.Role):

        await interaction.response.defer(ephemeral=True)

        if interaction.guild is None:
            await interaction.response.send_message("Este comando não pode ser usado em mensagens privadas.", ephemeral=True)
            return
        
        members_with_role = [member for member in interaction.guild.members if cargo in member.roles]

        for member in members_with_role:
            try:
                await member.add_roles(addcargo)
                print(f"Cargo {addcargo.name} adicionado a {member.display_name}")
                await asyncio.sleep(2)
            except discord.Forbidden:
                print(f"Falha ao adicionar {addcargo.name} ao {member.display_name}")

        await interaction.response.send_message(f"Cargo {addcargo.name} adicionado a {len(members_with_role)} membros.", ephemeral=True)

    @addrole.error
    async def addrole_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message("Você não tem permissão para usar este comando. Adicione o cargo <@&942666939686334524> para utilizar este comando.", ephemeral=True)
        else:
            print(f'Error in teste command: {error}')

async def setup(bot):
    await bot.add_cog(Limpa(bot))