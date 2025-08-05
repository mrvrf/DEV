import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import discord.ui

class ImageModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Enviar Imagem")
        self.image_url = discord.ui.TextInput(
            label="Link da Imagem",
            placeholder="Cole o link da imagem aqui...",
            required=True,
            style=discord.TextStyle.short
        )
        self.add_item(self.image_url)

class ModalButton(discord.ui.View):
    def __init__(self, member, message):
        super().__init__()
        self.member = member
        self.message = message

    @discord.ui.button(label="Enviar Imagem", style=discord.ButtonStyle.primary)
    async def send_modal(self, interaction: discord.Interaction, button: discord.ui.Button):
        modal = ImageModal()
        await interaction.response.send_modal(modal)

        try:
            await modal.wait()
            
            approval_channel = interaction.guild.get_channel(1318400984531210281)
            approval_embed = discord.Embed(
                title="Aprovação de Imagem",
                description=f"Enviado por: {self.member.mention}\nMensagem: {self.message}",
                color=discord.Color.gold()
            )
            approval_embed.set_image(url=modal.image_url.value)
            
            view = ApprovalView(self.member)
            await approval_channel.send(embed=approval_embed, view=view)
            await interaction.followup.send("Imagem enviada para aprovação!", ephemeral=True)
        except TimeoutError:
            await interaction.followup.send("Tempo esgotado!", ephemeral=True)

class ApprovalView(discord.ui.View):
    def __init__(self, member):
        super().__init__(timeout=None)
        self.member = member

    @discord.ui.button(label="APROVAR", style=discord.ButtonStyle.green)
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"Aprovado: {self.member.mention}", ephemeral=True)
        self.stop()

    @discord.ui.button(label="DESAPROVAR", style=discord.ButtonStyle.red)
    async def disapprove(self, interaction: discord.Interaction, button: discord.ui.Button):
        role_id = 1388632745248428132
        role = interaction.guild.get_role(role_id)
        await self.member.add_roles(role)
        await interaction.response.send_message(f"Desaprovado: {self.member.mention}", ephemeral=True)
        self.stop()

class Cobrar(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="cobrar", description="Envia cobrança para um cargo específico")
    @app_commands.describe(message="Mensagem da cobrança", role="Cargo para cobrar")
    async def cobrar(self, interaction: discord.Interaction, message: str, role: discord.Role):
        await interaction.response.defer(ephemeral=True)
        
        for member in role.members:
            if not member.bot:
                try:
                    dm_embed = discord.Embed(
                        title="Cobrança",
                        description=message,
                        color=discord.Color.blue()
                    )
                    view = ModalButton(member, message)
                    await member.send(embed=dm_embed, view=view)
                except discord.Forbidden:
                    await interaction.followup.send(f"Não foi possível enviar mensagem para {member.mention}", ephemeral=True)
        
        await interaction.followup.send(f"Cobrança enviada para {len(role.members)} membros do cargo {role.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Cobrar(bot))