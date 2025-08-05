import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import asyncio

class Aviso(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="aviso", description="Envia mensagem privada para membros com um cargo específico.")
    @app_commands.guild_only()
    @app_commands.describe(cargo="Cargo para enviar a mensagem", mensagem="Mensagem a ser enviada", tipo="Tipo de aviso", imagem="Imagem")
    @app_commands.checks.has_role(1325386396214628454)
    @app_commands.choices(tipo=[
        app_commands.Choice(name="Aviso", value="Aviso"),
        app_commands.Choice(name="Reunião", value="Reunião"),
        app_commands.Choice(name="Boss de guilda", value="Boss de Guilda"),
        app_commands.Choice(name="Treino", value="Treino"),
        app_commands.Choice(name="GvG", value="GvG"),
        app_commands.Choice(name="GvG Obrigatoria", value="Obrigatoria")
    ])
    async def aviso(self, interaction: discord.Interaction, cargo: discord.Role, mensagem: str, tipo: app_commands.Choice[str], imagem: discord.Attachment = None):
        guild = interaction.guild

        if tipo.value == "Treino":
            tipotitulo = "Treino :crossed_swords:"
            tipocor = 0x00FFFF
        elif tipo.value == "Reunião":
            tipotitulo = "Reunião :calendar_spiral:"
            tipocor = 0x9900FF
        elif tipo.value == "Boss de Guilda":
            tipotitulo = "Boss de Guilda :dragon:"
            tipocor = 0x274E13
        elif tipo.value == "GvG":
            tipotitulo = "GvG <a:gvg:1149917011456040973>"
            tipocor = 0x000000
        elif tipo.value == "Obrigatoria":
            tipotitulo = "<a:gvg:1149917011456040973> CALL OBRIGATÓRIA - GVG <a:gvg:1149917011456040973>"
            tipocor = 0xFF0000
        else:
            tipotitulo = "Aviso <:gooraStare:978714387349127198>"
            tipocor = 0xFFFF00


        # Log the command usage
        current_time = datetime.now().strftime("%d/%m/%Y | %H:%M")
        log_embed = discord.Embed(
            title="**Comando Executado**",
            description=f"**Comando:** */aviso*\n**Hora:** {current_time}",
            color=0xFFFFFF
        )
        log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)
        print(f"Aviso iniciado por {interaction.user.display_name} - {mensagem}")



        log_channel = interaction.guild.get_channel(1318401148151009391)
        await log_channel.send(embed=log_embed)

        war_room_log = interaction.guild.get_channel(1126288833655349308)
        await war_room_log.send(f":warning: **Aviso** (**{tipotitulo}**) enviado para **{cargo.name}** por {interaction.user.mention}")

        # Defer the response to avoid timeout
        await interaction.response.defer(ephemeral=True)

        if tipo.value == "Obrigatoria":
            aviso_sala1 = interaction.guild.get_channel(929466094077509662) #avisos
            aviso_sala2 = interaction.guild.get_channel(946208313123667968) #ping-pvp
            await aviso_sala1.send(f"# {cargo.mention} {mensagem}")
            await asyncio.sleep(1)
            await aviso_sala2.send(f"# <@&929480758328975381> <@&929344073221935104> <@&935733958266716200> <@&1206381250064158740> {mensagem}")
            await asyncio.sleep(1)
            await aviso_sala2.send(f"# <@&929480758328975381> <@&929344073221935104> <@&935733958266716200> <@&1206381250064158740> {mensagem}")
            await asyncio.sleep(1)
            await aviso_sala2.send(f"# <@&929480758328975381> <@&929344073221935104> <@&935733958266716200> <@&1206381250064158740> {mensagem}")
            await asyncio.sleep(1)
        else:
            await asyncio.sleep(1)

        successful_members = []
        failed_members = []

        for idx, member in enumerate(cargo.members):
            if not member.bot:
                embed = discord.Embed(title=f"{tipotitulo}", description=f"**{mensagem}**\n", color=tipocor)
                if imagem:
                    embed.set_image(url=imagem)
                current_time = datetime.now().strftime("%H:%M")
                if member.avatar:
                    embed.set_footer(text=f"Aviso recebido por: {member.display_name} às {current_time}", icon_url=member.avatar.url)
                else:
                    embed.set_footer(text=f"Aviso recebido por: {member.display_name} às {current_time}")
                
                try:
                    await member.send(embed=embed)
                    successful_members.append(member.display_name)
                    print(f'(Aviso) Mensagem enviada para {member.display_name}')

                    # Remove this block to avoid sending the log multiple times
                    if len(successful_members) % 20 == 0:
                         log_embed = discord.Embed(
                             title="**Atualização do Aviso**",
                             description=f"{len(successful_members)} membros notificados.",
                             color=0xFFFF00
                         )
                         log_embed.add_field(name="Membros notificados :white_check_mark:", value="\n".join(successful_members[-20:]), inline=False)
                         log_channel = guild.get_channel(1318400984531210281)
                         await log_channel.send(embed=log_embed)

                except Exception as e:
                    failed_members.append(member.display_name)
                    print(f'(Aviso) Não foi possível enviar mensagem para {member.display_name}: {e}')

                await asyncio.sleep(3.5)

        if len(successful_members) % 20 != 0 and successful_members:
            log_embed = discord.Embed(
                title="**Atualização do Aviso**",
                description=f"{len(successful_members)} membros notificados.",
                color=0xFFFF00
            )
            log_embed.add_field(name="Membros notificados :white_check_mark:", value="\n".join(successful_members[-20:]), inline=False)
            log_embed.add_field(name="Membros com erro :x:", value="\n".join(failed_members), inline=False)
            log_channel = guild.get_channel(1318400984531210281)
            log_embed.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y | %H:%M')}")
            await log_channel.send(embed=log_embed)

        final_embed = discord.Embed(
            title=f"**Resultado do Aviso - {tipotitulo}**",
            description=f"Total de membros processados: {len(successful_members) + len(failed_members)}",
            color=0x00FF00 if not failed_members else 0xFF0000
        )
        final_embed.add_field(
            name=f"Aviso para {cargo.name}", 
            value=f":white_check_mark: Mensagens enviadas com sucesso: **({len(successful_members)})**\n:cross_mark: Mensagens NÃO enviadas: **({len(failed_members)})**\n", #if failed_members else successful_members,
            inline=False
        )
        final_embed.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y | %H:%M')}")

        log_channel = self.bot.get_channel(1318400984531210281)
        await log_channel.send(embed=final_embed)
        await interaction.user.send(embed=final_embed)

        await interaction.followup.send(embed=final_embed, ephemeral=True)

    @aviso.error
    async def aviso_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(f"Você não tem permissão para usar este comando. Adicione o cargo <@&1325386396214628454> para utilizar este comando.", ephemeral=True)
        else:
            print(f'Error in aviso command: {error}') 

async def setup(bot):
    await bot.add_cog(Aviso(bot))