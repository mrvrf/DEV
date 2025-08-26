import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime

class Mover(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="mover", description="Move todos os jogadores de um canal de voz para outro.")
    @app_commands.guild_only()
    @app_commands.checks.has_role(1325386396214628454)
    @app_commands.describe(canal_origem="Canal de voz de origem", canal_destino="Canal de voz de destino")
    @app_commands.checks.has_permissions(move_members=True)
    async def mover(self, interaction: discord.Interaction, canal_origem: discord.VoiceChannel, canal_destino: discord.VoiceChannel):


        await interaction.response.defer(ephemeral=True)

        current_time = datetime.now().strftime("%d/%m/%Y | %H:%M")

        log_embed = discord.Embed(
            title="**Comando Executado**",
            description=f"**Comando:** */mover*\n**Hora:** {current_time}",
            color=0xFFFFFF
        )
        log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
        print(f"Mover iniciado por {interaction.user.display_name} - {canal_origem} para {canal_destino}")

        log_channel = interaction.guild.get_channel(1318401148151009391)
        await log_channel.send(embed=log_embed)

        if canal_origem == canal_destino:
            await interaction.response.send_message("Os canais de origem e destino não podem ser iguais.", ephemeral=True)
            return

        members = canal_origem.members
        if not members:
            await interaction.response.send_message("Não há membros no canal de origem.", ephemeral=True)
            return

        moved_members = []
        for member in members:
            try:
                await member.move_to(canal_destino)
                moved_members.append(member.display_name)
            except Exception as e:
                await interaction.response.send_message(f"Erro ao mover {member.display_name}: {e}", ephemeral=True)
                return

        embed = discord.Embed(
            title=f"Resultado do Mover",
            description=f"{len(moved_members)} membros movidos",
            color=0x00FF00
        )
        embed.add_field(name="Membros movidos:", value="\n".join(moved_members), inline=False)
        embed.add_field(name="Canal de origem", value=canal_origem.mention, inline=False)
        embed.add_field(name="Canal de destino", value=canal_destino.mention, inline=False)
        embed.set_footer(text=f"Movido por {interaction.user.display_name} - {current_time}", icon_url=interaction.user.avatar.url)

        log_botmerizinha = self.bot.get_channel(1318400984531210281)
        await log_botmerizinha.send(embed=embed)
        await interaction.followup.send(f"{len(moved_members)} membros movidos do canal {canal_origem} para o canal {canal_destino}", ephemeral=True)

    @mover.error
    async def mover_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Ocorreu um erro: {error}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Mover(bot))