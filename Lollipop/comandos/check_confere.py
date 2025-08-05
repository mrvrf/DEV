import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import asyncio

class CConfere(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="check_confere", description="Libera o membro por mensagem privada.")
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

        # Envia o log para um canal específico
        log_channel = interaction.guild.get_channel(1318401148151009391)
        await log_channel.send(embed=log_embed)

        confere = interaction.guild.get_channel(1318400984531210281)
        await confere.send(f":white_check_mark: **Confere** iniciado por {interaction.user.mention}")

        mention_ids = [int(user_id.strip('<@!>')) for user_id in membros.split() if user_id.startswith('<@') and user_id.endswith('>')]
        
        if not mention_ids:
            await interaction.response.send_message("Por favor, mencione os membros para enviar a mensagem.", ephemeral=True)
            return
        
        # Inicializa as listas para rastreamento de membros
        successful_members = []
        failed_members = []
        pending_approval = []

        # Defer the response to avoid timeout
        await interaction.response.defer(ephemeral=True)

        # Process members based on role
        for user_id in mention_ids:
            member = interaction.guild.get_member(user_id)
            if member and not member.bot:
                specific_role_id = 1388632745248428132
                specific_role = discord.utils.get(interaction.guild.roles, id=specific_role_id)

                if specific_role in member.roles:
                    # Add to pending approval list
                    pending_approval.append(member)
                else:
                    # Send DM automatically for members without role
                    try:
                        dm_embed = discord.Embed(
                            title="Mensagem Privada",
                            description=mensagem,
                            color=0x00FF00
                        )
                        await member.send(embed=dm_embed)
                        successful_members.append(member)
                    except discord.Forbidden:
                        failed_members.append(member)

        # Process members that need approval
        if pending_approval:
            approval_embed = discord.Embed(
                title="Aprovação Necessária",
                description=f"Os seguintes membros estão taxados (DESAPROVADO):\n{', '.join([m.mention for m in pending_approval])}\nDeseja enviar a mensagem privada?",
                color=0x00FF00
            )

            class ApprovalView(discord.ui.View):
                def __init__(self):
                    super().__init__()
                    self.result = None

                @discord.ui.button(label="APROVAR", style=discord.ButtonStyle.green)
                async def approve(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                    self.result = True
                    await interaction_button.response.defer()
                    self.stop()

                @discord.ui.button(label="DESAPROVAR", style=discord.ButtonStyle.red)
                async def disapprove(self, interaction_button: discord.Interaction, button: discord.ui.Button):
                    self.result = False
                    await interaction_button.response.defer()
                    self.stop()

            view = ApprovalView()
            await interaction.followup.send(embed=approval_embed, view=view, ephemeral=True)
            await view.wait()

            if view.result:
                for member in pending_approval:
                    try:
                        dm_embed = discord.Embed(
                            title="Participar :white_check_mark:",
                            description=f"**{mensagem}**",
                            color=0x00FF00
                        )
                        await member.send(embed=dm_embed)
                        successful_members.append(member)
                    except discord.Forbidden:
                        failed_members.append(member)

        # Send a summary of the operation
        summary_message = f"**Resumo:**\n"
        if successful_members:
            summary_message += f"Mensagens enviadas para: {', '.join([m.mention for m in successful_members])}\n"
        if failed_members:
            summary_message += f"Falha ao enviar mensagens para: {', '.join([m.mention for m in failed_members])}\n"
        await confere.send(summary_message, ephemeral=True)

async def setup(bot):
    await bot.add_cog(CConfere(bot))
