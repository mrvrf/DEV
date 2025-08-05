import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View
from datetime import datetime

class CounterView(View):
    def __init__(self):
        super().__init__(timeout=None)
        self.counter1 = 0
        self.counter2 = 0

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="<:GooraDeathStare:978714546564907048>")
    async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.counter1 += 1
        await self.update_embed(interaction)

    @discord.ui.button(label="", style=discord.ButtonStyle.primary, emoji="<:Shai:1231643630855393370>")
    async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.counter2 += 1
        await self.update_embed(interaction)

    async def update_embed(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Teste",
            description=f"<:GooraDeathStare:978714546564907048> **Contador 1:** {self.counter1}\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003<:Shai:1231643630855393370> **Contador 2:** {self.counter2}",
            color=0x00FF00
        )
        await interaction.response.edit_message(embed=embed, view=self)

class Wip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="wip", description="NAO SEI O QUE FAZ")
    @app_commands.guild_only()
    async def wip(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Teste",
            description=f"<:GooraDeathStare:978714546564907048> **Contador 1:** 0\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003\u2003<:Shai:1231643630855393370> **Contador 2:** 0",
            color=0x00FF00
        )
        view = CounterView()
        await interaction.response.send_message(embed=embed, view=view)




class Teste(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="teste", description="Teste de integração")
    @app_commands.checks.has_role(1325386396214628454)
    @app_commands.guild_only()
    async def teste(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        current_time = datetime.now().strftime("%d/%m/%Y | %H:%M")
        commands_list = "\n".join([command.name for command in self.bot.tree.get_commands()])
        message = f"**Online - Comandos disponíveis\n{current_time}\nComandos carregados:**\n{commands_list}"
        print(f"Enviando teste para {interaction.user.display_name}")

        await interaction.followup.send(message)

    @teste.error
    async def teste_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message(f"Você não tem permissão para usar este comando. Adicione o cargo <@&1325386396214628454> para utilizar este comando.", ephemeral=True)
        else:
            print(f'Error in teste command: {error}')

    @app_commands.command(name="status", description="teste")
    @app_commands.checks.has_role(1325386396214628454)
    @app_commands.guild_only()
    async def status(self, interaction: discord.Interaction):

        role1 = interaction.guild.get_role(1210354501870166077)
        role2 = interaction.guild.get_role(1210354582048473088)
        role3 = interaction.guild.get_role(1210354616840093796)
        role4 = interaction.guild.get_role(1210354659378860083)

        members = [f"> {member.display_name}" for member in role1.members]
        members2 = [f"> {member.display_name}" for member in role2.members]
        members3 = [f"> {member.display_name}" for member in role3.members]
        members4 = [f"> {member.display_name}" for member in role4.members]

        members.sort()
        members2.sort()
        members3.sort()
        members4.sort()

        members_list = "\n".join(members) if members else "Nenhum membro encontrado."
        members_list2 = "\n".join(members2) if members2 else "Nenhum membro encontrado."
        members_list3 = "\n".join(members3) if members3 else "Nenhum membro encontrado."
        members_list4 = "\n".join(members4) if members4 else "Nenhum membro encontrado."

        embed = discord.Embed(
            title=f"teste",
            description=f"{role1.name} - {role2.name} - {role3.name} - {role4.name}",
            color=role1.color
        )
        embed.add_field(name=f"{role1.name}", value=members_list, inline=True)
        embed.add_field(name=f"{role2.name}", value=members_list2, inline=True)
        embed.add_field(name=f"{role3.name}", value=members_list3, inline=True)
        embed.add_field(name=f"{role4.name}", value=members_list4, inline=True)
        embed.set_footer(text=f"Solicitado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)        

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="raid", description="Lista de membros no cargo")
    @app_commands.checks.has_role(1325386396214628454)
    @app_commands.guild_only()
    async def raid(self, interaction: discord.Interaction, role: discord.Role):

        members = [f"> {member.display_name}" for member in role.members]
        members.sort()
        members_list = "\n".join(members) if members else "Nenhum membro encontrado."

        embed = discord.Embed(
            title=f"Membros no cargo {role.name}",
            description=members_list,
            color=role.color
        )
        embed.add_field(name=f"Total de membros: {len(members)}", value="", inline=False)
        embed.set_footer(text=f"Solicitado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Teste(bot))
    #await bot.add_cog(Wip(bot))