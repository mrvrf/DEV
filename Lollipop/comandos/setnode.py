import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import asyncio

def cargo_server(server_id: int, role_id: int):
    async def predicate(interaction: discord.Interaction) -> bool:
        guild = interaction.client.get_guild(server_id)
        if guild is None:
            await interaction.response.send_message("Não foi possível encontrar o servidor especificado.", ephemeral=True)
            return False

        member = guild.get_member(interaction.user.id)
        if member is None:
            await interaction.response.send_message("Você não é membro do servidor especificado.", ephemeral=True)
            return False

        role = guild.get_role(role_id)
        if role is None:
            await interaction.response.send_message("Não foi possível encontrar o cargo especificado.", ephemeral=True)
            return False

        if role in member.roles:
            return True

        await interaction.response.send_message(f"Você não tem permissão para usar este comando. É necessário o cargo {role.name}.", ephemeral=True)
        return False
    return app_commands.check(predicate)

class Node(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_embed = None  # salva ultimo embed

    @app_commands.command(name="setnode", description="Envia informações da node para um cargo específico.")
    @app_commands.guild_only()
    @app_commands.describe(territorio="Qual território da node", servidores="Quais servidores para colocar participar", quantidade="Quantidade", cap="Cap")
    @app_commands.checks.has_role(1325386396214628454)
    @app_commands.choices(cap=[
        app_commands.Choice(name="Capado", value="Capado"),
        app_commands.Choice(name="Descapado", value="Descapado")
    ])
    @app_commands.choices(territorio=[
        app_commands.Choice(name="Balenos", value="Balenos"),
        app_commands.Choice(name="Serendia", value="Serendia"),
        app_commands.Choice(name="Calpheon", value="Calpheon"),
        app_commands.Choice(name="Mediah", value="Mediah"),
        app_commands.Choice(name="Valencia", value="Valencia"),
        app_commands.Choice(name="Kamasylvia", value="Kamasylvia"),
        app_commands.Choice(name="Balenos/Serendia", value="Balenos/Serendia"),
        app_commands.Choice(name="Calpheon/Kamasylvia", value="Calpheon/Kamasylvia"),
        app_commands.Choice(name="Mediah/Valencia", value="Mediah/Valencia")
    ])
    async def setnode(self, interaction: discord.Interaction, territorio: app_commands.Choice[str], servidores: str, quantidade: str, cap: app_commands.Choice[str], cargo: discord.Role):

        log_embed = discord.Embed(
            title=f"**Comando Executado**",
            description=f"**Comando:** */setnode*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
            color=0xFFFFFF
        )
        log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
        print(f"Node {territorio.name} iniciada por {interaction.user.display_name}")

        log_channel = self.bot.get_channel(1318401148151009391)
        await log_channel.send(embed=log_embed)

        war_room_log = interaction.guild.get_channel(1126288833655349308)
        await war_room_log.send(f":warning: **Node** {territorio.name} iniciada por {interaction.user.mention} para {cargo.name}")

        embed = discord.Embed(
            title=f"Informação da Nodewar - {territorio.name}",
            color=0xFF9900
        )
        embed.add_field(name="**ATENÇÃO** :exclamation:", value="Isso é apenas um aviso de **ONDE** é a nodewar! **NÃO** coloque participar sem permissão.\n", inline=False)
        embed.add_field(name="**Servidores**", value=servidores, inline=False)
        embed.add_field(name="**Quantidade**", value=f"**{quantidade}** players", inline=False)
        embed.add_field(name=f"**{cap.value}**", value=f"", inline=False) 
        embed.add_field(name="", value="** * Entre TS 20:40h \n* lollipop.ts3guild.com.br \n* Senha: femboy**", inline=False)
        
        self.last_embed = embed

        await self.bot.change_presence(activity=discord.Game(name=f"Nodewar {territorio.name}"))
        print(f"Nodewar {territorio.name} iniciada")

        await interaction.response.send_message(embed=embed, ephemeral=True)

        successful_members = []
        failed_members = []

        for idx, member in enumerate(cargo.members):
            if not member.bot:
                current_time = datetime.now().strftime("%H:%M")
                if member.avatar:
                    embed.set_footer(text=f"Recebido por {member.display_name} às {current_time}", icon_url=member.avatar.url)
                else:
                    embed.set_footer(text=f"Recebido por {member.display_name} às {current_time}")
                
                try:
                    await member.send(embed=embed)
                    successful_members.append(member.display_name)
                    print(f'(Node) mensagem enviada para {member.display_name} - {member.name}')
                    
                    if len(successful_members) % 10 == 0:
                        log_embed = discord.Embed(
                            title="**Atualização da Node**",
                            description=f"{len(successful_members)} membros notificados.",
                            color=0xFFFF00
                        )
                        log_embed.add_field(name="Membros notificados :white_check_mark:", value="\n".join(successful_members[-10:]), inline=False)
                        log_channel = self.bot.get_channel(1318400984531210281)
                        await log_channel.send(embed=log_embed)
                        
                except Exception as e:
                    failed_members.append(member.display_name)
                    print(f'(Node) erro ao enviar mensagem para {member.display_name} - {member.name}: {e}')

                await asyncio.sleep(3.5)                

        if len(successful_members) % 10 != 0 and successful_members:
            log_embed = discord.Embed(
                title="**Atualização da Node**", 
                description=f"{len(successful_members)} membros notificados.",
                color=0xFFFF00
            )
            log_embed.add_field(name="Membros notificados :white_check_mark:", value="\n".join(successful_members[-10:]), inline=False)
            log_embed.add_field(name="Membros com erro :x:", value="\n".join(failed_members), inline=False)
            log_channel = self.bot.get_channel(1318400984531210281)
            log_embed.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y | %H:%M')}")
            await log_channel.send(embed=log_embed)

        final_embed = discord.Embed(
            title=f"**Resultado Node - {territorio.value}**",
            description=f"Total de membros processados: {len(successful_members) + len(failed_members)}",
            color=0x00FF00 if not failed_members else 0xFF0000
        )        
        final_embed.add_field(
            name=f"Nodewar {territorio.value} ({quantidade}) - {cap.value}", 
            value=f":white_check_mark: Mensagens enviadas com sucesso **({len(successful_members)})**\n:cross_mark: Mensagens enviadas com erro **({len(failed_members)})**\n",
            inline=False
        )
        final_embed.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y | %H:%M')}")
        
        #final_embed.add_field(
        #    name=f"Falhas no envio :x: ({len(failed_members)})", 
        #    value="\n".join(failed_members) if failed_members else "Nenhum",
        #    inline=False
        #)
        
        log_channel = self.bot.get_channel(1318400984531210281)
        await log_channel.send(embed=final_embed)
        await asyncio.sleep(14400)
        await self.bot.change_presence(activity=discord.Game(name="Aguardando guerra"))
        print (f"Nodewar {territorio.value} finalizada")

    @setnode.error
    async def setnode_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message(f"Você não tem permissão para usar este comando. Adicione o cargo <@&1325386396214628454> para utilizar este comando.", ephemeral=True)
        else:
            print(f'Error in teste command: {error}')        

    @app_commands.command(name="node", description="Ultima node registrada")
    @cargo_server(server_id=929343217915297812, role_id=929480758328975381)
    async def node(self, interaction: discord.Interaction):
        if self.last_embed:
            new_embed = self.last_embed.copy()
            current_time = datetime.now().strftime("%H:%M")
            new_embed.set_footer(text=f"Visualizado por {interaction.user.display_name} às {current_time}", icon_url=interaction.user.avatar.url)
            await interaction.response.send_message(embed=new_embed, ephemeral=False)
            
            log_embed = discord.Embed(
                title=f"**Comando Executado**",
                description=f"**Comando:** */node*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
                color=0xFFFFFF
            )
            log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
            
            log_channel = self.bot.get_channel(1318401148151009391)
            await log_channel.send(embed=log_embed)
        else:
            await interaction.response.send_message("Nenhuma node registrada ainda.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Node(bot))
    guild_id = 929343217915297812
    guild = discord.Object(id=guild_id)

    command = bot.tree.get_command("setnode", guild=guild)
    if command:
        command.default_permissions = discord.Permissions(administrator=True)

    await bot.tree.sync(guild=guild)
    print("Node commands registered in tree.")