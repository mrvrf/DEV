import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import asyncio

class Siege(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_embed = None  # Salvar último embed

    @app_commands.command(name="setsiege", description="Informações da siege para os membros")
    @app_commands.guild_only()
    @app_commands.describe(territorio="Nome do território", cap="Cap")
    @app_commands.checks.has_role(1325386396214628454)
    @app_commands.choices(territorio=[
        app_commands.Choice(name="Valencia", value="Valencia"),
        app_commands.Choice(name="Calpheon", value="Calpheon"),
        app_commands.Choice(name="Mediah", value="Mediah"),
        app_commands.Choice(name="Balenos", value="Balenos")
    ])
    @app_commands.choices(cap=[
        app_commands.Choice(name="Capado", value="Capado"),
        app_commands.Choice(name="Descapado", value="Descapado")
    ])
    async def setsiege(self, interaction: discord.Interaction, territorio: app_commands.Choice[str], cap: app_commands.Choice[str], role: discord.Role):
        # Cria embed
        servidor = f"{territorio.value}1"
        command_log_embed = discord.Embed(
            title=f"**Comando Executado**",
            description=f"**Comando:** */setsiege*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
            color=0xFFFFFF
        )
        command_log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
        print(f"Siege {territorio.value} iniciada por {interaction.user.display_name}")

        log_channel = self.bot.get_channel(1318401148151009391)  # Use your log channel ID
        await log_channel.send(embed=command_log_embed)

        war_room_log = interaction.guild.get_channel(1126288833655349308)
        await war_room_log.send(f":warning: **Siege** {territorio.value} iniciada por {interaction.user.mention} para {role.name}")

        embed = discord.Embed(
            title=f"Informação da Siege - {territorio.value}",
            # description=f"Coloque participar em: **{territorio}**",
            color=0xFF0000
        )
        embed.add_field(name="**ATENÇÃO** :exclamation:", value="Isso é apenas um aviso de **ONDE** é a siege! **NÃO** coloque participar sem permissão.\n", inline=False)
        embed.add_field(name="Servidor", value=servidor, inline=False)
        embed.add_field(name="Quantidade", value=f"**100** players", inline=False)
        embed.add_field(name=f"**{cap.value}**", value=f"", inline=False)
        embed.add_field(name="", value="** * Entre TS 20:40h \n* lollipop.ts3guild.com.br \n* Senha: femboy**", inline=False)
        
        # Store the embed for later use
        self.last_embed = embed

        # Update bot activity
        await self.bot.change_presence(activity=discord.Game(name=f"Siege {territorio.value}"))
        print (f"Siege {territorio.value} iniciada")

        # Send the embed to the channel (ephemeral, only visible to the user)
        await interaction.response.send_message(embed=embed, ephemeral=True)

        # Initialize lists for tracking members
        successful_members = []
        failed_members = []

        # Send private messages to all members with the specified role
        for idx, member in enumerate(role.members):
            if not member.bot:
                # Update the footer to include the recipient's information
                current_time = datetime.now().strftime("%H:%M")
                if member.avatar:
                    embed.set_footer(text=f"Recebido por {member.display_name} às {current_time}", icon_url=member.avatar.url)
                else:
                    embed.set_footer(text=f"Recebido por {member.display_name} às {current_time}")
                
                try:
                    await member.send(embed=embed)
                    successful_members.append(member.display_name)
                    print(f'(Siege) mensagem enviada para {member.display_name} - {member.name}')

                    if len(successful_members) % 20 == 0 and successful_members:
                        log_embed = discord.Embed(
                            title="**Atualização da Siege**",
                            description=f"{len(successful_members)} membros notificados.",
                            color=0xFFFF00
                        )
                        log_embed.add_field(name="Membros notificados :white_check_mark:", value="\n".join(successful_members[-20:]), inline=False)
                        log_channel = self.bot.get_channel(1318400984531210281)
                        await log_channel.send(embed=log_embed)

                except Exception as e:
                    failed_members.append(member.display_name)
                    print(f'(Siege) erro ao enviar mensagem para {member.display_name} - {member.name} {e}')
                
                await asyncio.sleep(3.5)

        if len(successful_members) % 20 != 0 and successful_members:
            log_embed = discord.Embed(
                title="**Atualização da Siege**",
                description=f"{len(successful_members)} membros notificados.",
                color=0xFFFF00
            )
            log_embed.add_field(name="Membros notificados :white_check_mark:", value="\n".join(successful_members[-20:]), inline=False)
            log_embed.add_field(name="Membros com erro :x:", value="\n".join(failed_members), inline=False)
            log_channel = self.bot.get_channel(1318400984531210281)
            log_embed.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y | %H:%M')}")
            await log_channel.send(embed=log_embed)

        final_embed = discord.Embed(
            title=f"**Resultado Siege - {territorio.value}**",
            description=f"Total de membros processados: {len(successful_members) + len(failed_members)}",
            color=0x00FF00 if failed_members else 0xFF0000
        )
        final_embed.add_field(
            name=f"Siege {territorio.value} - {cap.value}",
            value=f":white_check_mark: Mensagens enviadas com sucesso **({len(successful_members)})**\n:cross_mark: Mensagens enviadas com erro **({len(failed_members)})**\n",
            inline=False
        )
        final_embed.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y | %H:%M')}")
        
        log_channel = self.bot.get_channel(1318400984531210281)
        await log_channel.send(embed=final_embed)

        await asyncio.sleep(14400)
        await self.bot.change_presence(activity=discord.Game(name="Aguardando guerra"))
        print (f"Siege {territorio.value} finalizada")

    @setsiege.error
    async def setsiege_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message(f"Você não tem permissão para usar este comando. Adicione o cargo <@&1325386396214628454> para utilizar este comando.", ephemeral=True)
        else:
            print(f'Error in teste command: {error}')

                
    @app_commands.command(name="siege", description="Última siege registrada")
    async def siege(self, interaction: discord.Interaction):
        # Check if there is a stored embed
        if self.last_embed:
            # Clone the last embed to modify the footer without affecting stored embed
            new_embed = self.last_embed.copy()
            current_time = datetime.now().strftime("%H:%M")
            new_embed.set_footer(text=f"Visualizado por {interaction.user.display_name} às {current_time}", icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=new_embed, ephemeral=False)

            log_embed = discord.Embed(
                title=f"**Comando Executado**",
                description=f"**Comando:** */siege*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
                color=0xFFFFFF
            )
            log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
            
            log_channel = self.bot.get_channel(1318401148151009391)  # Use your log channel ID
            await log_channel.send(embed=log_embed)
        else:
            await interaction.response.send_message("Nenhuma siege registrada ainda.", ephemeral=True)

async def setup(bot):
    cog = Siege(bot)
    await bot.add_cog(cog)

    cog.setsiege.default_permissions = discord.Permissions(administrator=True)

    await bot.tree.sync()
    print("Siege commands registered in tree.")
