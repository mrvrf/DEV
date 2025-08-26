import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import asyncio

class Ccconfere(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ccconfere", description="Libera o membro por mensagem privada.")
    @app_commands.guild_only()
    @app_commands.describe(mensagem="Mensagem a ser enviada", membros="Membros liberados")
    @app_commands.checks.has_role(1325386396214628454)
    async def confere(self, interaction: discord.Interaction, mensagem: str, membros: str):
        log_embed = discord.Embed(
            title="**Comando Executado**",
            description=f"**Comando:** */confere*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
            color=0xFFFFFF
        )
        log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
        print(f"Confere iniciado por {interaction.user.display_name}")

        log_channel = interaction.guild.get_channel(1318401148151009391)
        await log_channel.send(embed=log_embed)

        confere = interaction.guild.get_channel(1119767862383476797)
        await confere.send(f":white_check_mark: **Confere** iniciado por {interaction.user.mention}")

    #    current_time = datetime.now().strftime("%H:%M")
        mention_ids = [int(user_id.strip('<@!>')) for user_id in membros.split() if user_id.startswith('<@') and user_id.endswith('>')]

        if not mention_ids:
            await interaction.response.send_message("Por favor, mencione os membros para enviar a mensagem.", ephemeral=True)
            return

        # Inicializa as listas para rastreamento de membros
        successful_members = []
        failed_members = []
        pending_approval = []
        disapproved_members = []  # New list for disapproved members


        # Defer the response to avoid timeout
        await interaction.response.defer(ephemeral=True)

        

        if not mention_ids:
            await interaction.followup.send("Por favor, mencione os membros para enviar a mensagem.", ephemeral=True)
            return

        for user_id in mention_ids:
            member = interaction.guild.get_member(user_id)
            embed_message = discord.Embed(
            title="Participar :white_check_mark:",
            description=f"**{mensagem}**",
            color=0x00FF00
            )
            embed_message.set_footer(text=f"Participar liberado para: {member.display_name}", icon_url=member.avatar.url if member.avatar else None)
            if member and not member.bot:  # Ignora bots
                rigidez_ids = [1375252320799166464, 1375252225512702034, 1375251715519152238]
                member_role = None
                #specific_role = any(discord.utils.get(member.roles, id=rigidez_id) for rigidez_id in rigidez_ids)  # Replace with your role ID

                for rigidez_id in rigidez_ids:
                    role = discord.utils.get(member.roles, id=rigidez_id)
                    if role:
                        member_role = role
                        break

                if member_role:
                    pending_approval.append(member)
                    approval_embed = discord.Embed(
                        title="Aprovação Necessária",
                        description=f"O membro {member.mention} possui o cargo **{member_role.name}**.\nDeseja liberar o participar?",
                        color=0xFF0000
                    )
                else:
                    try:

                #if specific_role:
                #    pending_approval.append(member)
                #else:
                #    try:
                        await member.send(embed=embed_message)
                        successful_members.append(member.display_name)
                        print(f'(Confere) Mensagem enviada para {member.display_name}')
                        await interaction.followup.send(f":white_check_mark: Participar liberado para {member.display_name}", ephemeral=True)
                    except Exception as e:
                        failed_members.append(member.display_name)
                        print(f'(Confere) Falha ao enviar mensagem para {member.display_name}: {e}')
                        await interaction.followup.send(f":x: Falha ao liberar participar para {member.display_name}", ephemeral=True)
                    await asyncio.sleep(2.0)

        if pending_approval:
            for member in pending_approval:
                approval_embed = discord.Embed(
                    title="Aprovação Necessária",
                    description=f"O membro {member.mention} possui o cargo **{member_role.name}**.\nDeseja liberar o participar?",
                    color=0xFF0000
                )

                class ApprovalView(discord.ui.View):
                    def __init__(self):
                        super().__init__()
                        self.value = None

                    @discord.ui.button(label="APROVAR", style=discord.ButtonStyle.green)
                    async def confirm(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                        self.value = True
                        self.stop()

                    @discord.ui.button(label="DESAPROVAR", style=discord.ButtonStyle.red)
                    async def cancel(self, button_interaction: discord.Interaction, button: discord.ui.Button):
                        self.value = False
                        self.stop()

                view = ApprovalView()
                msg = await interaction.followup.send(embed=approval_embed, view=view, ephemeral=True)
                await view.wait()

                if view.value:
                    try:
                        await member.send(embed=embed_message)
                        successful_members.append(member.display_name)
                        print(f'(Confere) Mensagem enviada para {member.display_name}')
                        await interaction.followup.send(f":white_check_mark: Participar liberado para {member.display_name}", ephemeral=True)
                    except Exception as e:
                        failed_members.append(member.display_name)
                        print(f'(Confere) Falha ao enviar mensagem para {member.display_name}: {e}')
                        await interaction.followup.send(f":x: Falha ao liberar participar para {member.display_name}", ephemeral=True)
                    await asyncio.sleep(2.0)

                if view.value == False:
                    disapproved_members.append(member.display_name)
                    print(f'(Confere) Mensagem não enviada para {member.display_name} - Desaprovado')
                    await interaction.followup.send(f":x: Participar não liberado para {member.display_name} - Desaprovado", ephemeral=True)
                    await asyncio.sleep(2.0)

        successful_members.sort()
        failed_members.sort()
        disapproved_members.sort()

        embed = discord.Embed(
            title="**Resultado do Confere**",
            description=f"**Confere enviado por:** {interaction.user.display_name}",
            color=0x00FF00
        )
        if successful_members:
            embed.add_field(name="Membros liberados :white_check_mark:", value="\n".join(successful_members), inline=False)
        if failed_members:
            embed.add_field(name="Membros NÃO liberados :x:", value="\n".join(failed_members), inline=False)
        if disapproved_members: 
            embed.add_field(name="Membros desaprovados :x:", value="\n".join(disapproved_members), inline=False)
        embed.add_field(name=f"Total de membros liberados: ({len(successful_members)})", value="", inline=False)
        embed.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y | %H:%M')}")
        print(f"Confere finalizado - {mensagem}")

        await interaction.followup.send(f":white_check_mark: **Confere** finalizado!", ephemeral=True)

        await interaction.followup.send(embed=embed, ephemeral=True)

        summary_channel = interaction.guild.get_channel(1119767862383476797)
        await summary_channel.send(embed=embed)

    @confere.error
    async def confere_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message(f"Você não tem permissão para usar este comando. Adicione o cargo <@&1325386396214628454> para utilizar este comando.", ephemeral=True)
        else:
            print(f'Error in teste command: {error}')

async def setup(bot):
    cog = Ccconfere(bot)
    await bot.add_cog(cog)

    command = bot.tree.get_command("confere")
    if command:
        command.default_permissions = discord.Permissions(administrator=True)

    await bot.tree.sync()
