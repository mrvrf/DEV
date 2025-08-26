import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import asyncio

class Lista(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='lista', description='Lista membros do canal de voz especificado')
    @app_commands.guild_only()
    @app_commands.checks.has_role(1326000068448489502)
    @app_commands.describe(canal_voz='O canal de voz para listar os membros', nome_lista='Nome da lista')
    async def list_members(self, interaction: discord.Interaction, canal_voz: discord.VoiceChannel, nome_lista: str):
        await interaction.response.defer(ephemeral=True)

        log_embed = discord.Embed(
            title=f"**Comando Executado**",
            description=f"**Comando:** */lista*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
            color=0xFFFFFF
        )
        log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

        log_channel = self.bot.get_channel(1318401148151009391)
        await log_channel.send(embed=log_embed)

        members = canal_voz.members

        await interaction.followup.send(f":track_next: Criando lista de membros do canal de voz {canal_voz.name}...", ephemeral=True)
        print("Criando lista...")
        await asyncio.sleep(3)

        members.sort(key=lambda member: member.display_name)

        member_info = []
        for idx, member in enumerate(members, start=1):
            if not member.bot:
                mute_status = "Microfone mutado" if member.voice.self_mute else "Microfone desmutado"
                deaf_status = "Audio mutado" if member.voice.self_deaf else "Audio desmutado"
                member_info.append(f"{idx}. {member.display_name} ({member.name}) - {mute_status}, {deaf_status}")

        current_time = datetime.now().strftime("%d_%m_%Y - %H_%M")

        file_name = f'lista {current_time}.txt'
        with open(file_name, 'w', encoding='utf-8') as file:
            file.write(f"Lista: {nome_lista}\n")
            file.write(f"Canal: {canal_voz.name}\n")
            file.write(f"Responsável: {interaction.user.display_name} - ({interaction.user.name})\n\n")
            for info in member_info:
                file.write(f"{info}\n")

        specific_channel_id = 1323553766087327817
        specific_channel = self.bot.get_channel(specific_channel_id)
        if specific_channel:
            await specific_channel.send(file=discord.File(file_name))
            await interaction.followup.send(":bar_chart: Lista enviada com sucesso. https://discord.com/channels/929343217915297812/1323553766087327817", ephemeral=True)
            print(f"Lista enviada para {specific_channel.name} executado por {interaction.user.display_name}")
        else:
            await interaction.followup.send(":no_entry_sign: Canal não encontrado.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Lista(bot))

    guild_id = 929343217915297812
    guild = discord.Object(id=guild_id)

    command = bot.tree.get_command("lista", guild=guild)
    if command:
        command.default_permissions = discord.Permissions(administrator=True)

    await bot.tree.sync(guild=guild)