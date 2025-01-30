import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from datetime import datetime

class PMensagem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pm_all", description="Envia uma mensagem privada para membros com um cargo específico.")
    @app_commands.guild_only()
    @app_commands.checks.has_role(1325386396214628454)
    @app_commands.describe(opt="Escolha entre 'todos' ou 'online'", cargo="Cargo para enviar a mensagem", mensagem="Mensagem a ser enviada")
    @app_commands.choices(opt=[
        app_commands.Choice(name="todos", value="todos"),
        app_commands.Choice(name="online", value="online")
    ])
    async def pm_all(self, interaction: discord.Interaction, opt: app_commands.Choice[str], cargo: discord.Role, mensagem: str):

        log_embed = discord.Embed(
            title="**Comando Executado**",
            description=f"**Comando:** */pm_all*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
            color=0xFFFFFF
        )
        log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
        print(f"PM_all iniciado por {interaction.user.display_name} - ({mensagem})")

        log_channel = interaction.guild.get_channel(1318401148151009391)
        await log_channel.send(embed=log_embed)

        await interaction.response.defer(ephemeral=True)

        members = cargo.members
        if opt.value == "online":
            members = [member for member in members if member.status != discord.Status.offline]

        successful_members = []
        failed_members = []

        for member in members:
            if not member.bot:
                try:
                    await member.send(mensagem)
                    successful_members.append(member.display_name)
                    print(f'(PM_A) Mensagem enviada para {member.display_name}')
                except Exception as e:
                    failed_members.append(member.display_name)
                    print(f'(PM_A) Falha ao enviar mensagem para {member.display_name}: {e}')

                await asyncio.sleep(3.5)

        await interaction.followup.send(f"Mensagens enviadas para {len(successful_members)} membros. Falha ao enviar para {len(failed_members)} membros.", ephemeral=True)

    @pm_all.error
    async def pm_all_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message(f"Você não tem permissão para usar este comando. Adicione o cargo <@&1325386396214628454> para utilizar este comando.", ephemeral=True)
        else:
            print(f'Error in teste command: {error}')

    @app_commands.command(name="pm", description="Envia uma mensagem privada para um membro específico.")
    @app_commands.guild_only()
    @app_commands.checks.has_role(1325386396214628454)
    @app_commands.describe(membros="Membros para enviar a mensagem", mensagem="Mensagem a ser enviada")
    async def pm(self, interaction: discord.Interaction, membros: str, mensagem: str):

        log_embed = discord.Embed(
            title="**Comando Executado**",
            description=f"**Comando:** */pm*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
            color=0xFFFFFF
        )
        log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
        print(f"PM iniciado por {interaction.user.display_name} - ({mensagem})")

        log_channel = interaction.guild.get_channel(1318401148151009391)
        await log_channel.send(embed=log_embed)    
        
        mention_ids = [int(user_id.strip('<@!>')) for user_id in membros.split() if user_id.startswith('<@') and user_id.endswith('>')]
        
        if not mention_ids:
            await interaction.response.send_message("Por favor, mencione os membros para enviar a mensagem.", ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)

        responses = []
        for user_id in mention_ids:
            member = interaction.guild.get_member(user_id)
            if member and not member.bot:
                try:
                    await member.send(mensagem)
                    responses.append(f"Mensagem enviada para {member.display_name}.")
                    print(f'(PM) Mensagem enviada para {member.display_name} por {interaction.user.display_name}')
                except Exception as e:
                    responses.append(f"Falha ao enviar mensagem para {member.display_name}: {e}")
                    print(f'(PM) Falha ao enviar mensagem para {member.display_name}: {e}')

        await interaction.followup.send("\n".join(responses), ephemeral=True)

    @pm.error
    async def pm_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message(f"Você não tem permissão para usar este comando. Adicione o cargo <@&1325386396214628454> para utilizar este comando.", ephemeral=True)
        else:
            print(f'Error in teste command: {error}')

async def setup(bot):
    await bot.add_cog(PMensagem(bot))