import discord
from discord.ext import commands
from discord import app_commands

class Ajuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name='ajuda', description='Mostra a lista de comandos')
    @app_commands.guild_only()
    async def ajuda(self, interaction: discord.Interaction):
        embed1 = discord.Embed(
            title="Comando /aviso",
            description="Envia um aviso como mensagem privada para membros com um cargo específico.",
            color=0xFF6500
        )
        embed1.add_field(name="Uso", value="/aviso (cargo) (mensagem) (tipo)", inline=False)
        embed1.add_field(name="Exemplo", value="/aviso cargo: **(Registrado_Canute)** mensagem: **(REUNIÃO HOJE 22H)** tipo: **(Reunião)", inline=False)

        embed2 = discord.Embed(
            title="Comando /lista",
            description="Cria uma lista de membros em um canal de voz com seus nomes atuais e status de mudo/surdo.",
            color=0xFF6500
        )
        embed2.add_field(name="Uso", value="/lista (canal de voz) (nome para a lista)", inline=False)
        embed2.add_field(name="Exempo", value="/lista canal: **(guild-01)** nome: **(TREINO CASTELO)**", inline=False)

        embed3 = discord.Embed(
            title="Comando /confere",
            description="Libera o membro via confere por mensagem privada.",
            color=0xFF6500
        )
        embed3.add_field(name="Uso", value="/confere (mensagem) (membros)", inline=False)
        embed3.add_field(name="Exemplo", value="/confere msg: **(DA PARTICIPAR AI DOG)** membros: **(@Membro1 @Membro2 @Membro3)**", inline=False)

        embed4 = discord.Embed(
            title="Comando /setnode",
            description="Envia as informações da node do dia para os membros com um cargo específico.",
            color=0xFF6500
        )
        embed4.add_field(name="Uso", value="/setnode (territorio) (servidores) (quantidade) (cap) (role)", inline=False)
        embed4.add_field(name="Exemplo", value="/setnode territorio: **(Balenos)** servidores: **(Balenos1)** quantidade: **(50)** cap: **(Capado)** role: **(NodeSeg)**", inline=False)

        embed5 = discord.Embed(
            title="Comando /setsiege",
            description="Envia as informações da siege da semana para os membros com um cargo específico.",
            color=0xFF6500
        )
        embed5.add_field(name="Uso", value="/setsiege (territorio) (servidor) (cap) (role)", inline=False)
        embed5.add_field(name="Exemplo", value="/setsiege territorio: **(Valencia)** servidor: **(Valencia)** cap: **(Descapado)** role: **(Siege)**", inline=False)

        await interaction.response.send_message(embeds=[embed1, embed2, embed3, embed4, embed5], ephemeral=True)
        print(f"Ajuda enviada para {interaction.user.display_name}")

async def setup(bot):
    await bot.add_cog(Ajuda(bot))