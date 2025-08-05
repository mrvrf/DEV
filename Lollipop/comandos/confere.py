import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import asyncio

class Confere(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="confere", description="Libera o membro por mensagem privada.")
    @app_commands.guild_only()
    @app_commands.describe(mensagem="Mensagem a ser enviada", membros="Membros liberados")
    @app_commands.checks.has_role(1325386396214628454)
    async def confere(self, interaction: discord.Interaction, mensagem: str, membros: str):
        # Cria embed para logar o uso do comando
        log_embed = discord.Embed(
            title="**Comando Executado**",
            description=f"**Comando:** */confere*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
            color=0xFFFFFF
        )
        log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
        print(f"Confere iniciado por {interaction.user.display_name}")
        print(f"Confere = {mensagem}")

        # Envia o log para um canal específico
        log_channel = interaction.guild.get_channel(1318401148151009391)
        await log_channel.send(embed=log_embed)

        confere = interaction.guild.get_channel(1119767862383476797)
        await confere.send(f":white_check_mark: **Confere** iniciado por {interaction.user.mention}")



        current_time = datetime.now().strftime("%H:%M")
        mention_ids = [int(user_id.strip('<@!>')) for user_id in membros.split() if user_id.startswith('<@') and user_id.endswith('>')]
        
        if not mention_ids:
            await interaction.response.send_message("Por favor, mencione os membros para enviar a mensagem.", ephemeral=True)
            return
        
        # Inicializa as listas para rastreamento de membros
        successful_members = []
        failed_members = []

        # Defer the response to avoid timeout
        await interaction.response.defer(ephemeral=True)

        # Envia mensagens privadas para todos os membros mencionados
        for user_id in mention_ids:
            member = interaction.guild.get_member(user_id)
            if member and not member.bot:  # Ignora bots
                embed_message = discord.Embed(
                    title="Participar :white_check_mark:",
                    description=f"**{mensagem}**",
                    color=0x00FF00
                )
                embed_message.set_footer(text=f"Participar liberado para: {member.display_name}", icon_url=member.avatar.url if member.avatar else None)
                try:
                    await member.send(embed=embed_message)
                    successful_members.append(member.display_name)
                    print(f'(Confere) Mensagem enviada para {member.display_name}')
                    await interaction.followup.send(f":white_check_mark: Participar liberado para {member.display_name}", ephemeral=True)
                except Exception as e:
                    failed_members.append(member.display_name)
                    print(f'(Confere) Falha ao enviar mensagem para {member.display_name}: {e}')
                    await interaction.followup.send(f":x: Falha ao liberar participar para {member.display_name}", ephemeral=True)
                
                # Aguarda 1 segundo entre as mensagens
                await asyncio.sleep(2.0)

        successful_members.sort()
        failed_members.sort()

        # Cria embed com o resumo do envio das mensagens
        embed = discord.Embed(
            title="**Resultado do Confere**",
            description=f"**Confere enviado por:** {interaction.user.display_name}",
            color=0x00FF00
        )        
        if successful_members:
            embed.add_field(name="Membros liberados :white_check_mark:", value="\n".join(successful_members), inline=False)
        if failed_members:
            embed.add_field(name="Membros NÃO liberados :x:", value="\n".join(failed_members), inline=False)
        embed.add_field(name=f"Total de membros liberados: ({len(successful_members)})", value="", inline=False)
        embed.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y | %H:%M')}")
        print(f"Confere finalizado - {mensagem}")

        await interaction.followup.send(f":white_check_mark: **Confere** finalizado!", ephemeral=True)
        
        # Envia a resposta do comando
        await interaction.followup.send(embed=embed, ephemeral=True)

        # Envia o resumo do envio das mensagens para um canal específico
        summary_channel = interaction.guild.get_channel(1119767862383476797)
        await summary_channel.send(embed=embed)

    @confere.error
    async def confere_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message(f"Você não tem permissão para usar este comando. Adicione o cargo <@&1325386396214628454> para utilizar este comando.", ephemeral=True)
        else:
            print(f'Error in teste command: {error}')

async def setup(bot):
    cog = Confere(bot)
    await bot.add_cog(cog)

    # Define permissões padrão para comandos
    command = bot.tree.get_command("confere")
    if command:
        command.default_permissions = discord.Permissions(administrator=True)

    await bot.tree.sync()
