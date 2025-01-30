import discord
from discord.ext import commands
from discord import app_commands
import datetime

intents = discord.Intents.default()
intents.message_content = True  # Habilita a intenção para leitura de mensagens
intents.members = True  # Habilita a intenção para ver membros

# Cria o bot de comandos tradicionais
bot = commands.Bot(command_prefix="!", intents=intents)
LOG_CHANNEL_ID = 1317197472602263573

@bot.event
async def on_ready():
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Game(name="Betando lolis")
    )
    print(f'Bot {bot.user} está online!')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')
    await log_command(ctx, 'ping')

# Classe para comandos de barra
class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        guild = discord.Object(id=1316995307493392414)  # Substitua pelo ID do seu servidor
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)

client = MyClient()

@client.event
async def on_ready():
    print(f'Bot {client.user} está online!')

@client.tree.command(name="aviso", description="Envia mensagem privada para membros com um cargo específico.")
@app_commands.checks.has_permissions(administrator=True)
async def aviso(interaction: discord.Interaction, cargo: discord.Role, mensagem: str):
    guild = interaction.guild
    for member in cargo.members:
        if not member.bot:
            embed = discord.Embed(title="Aviso", description=f"**{mensagem}**", color=0xFF0000)
            embed.set_footer(text=f"Mensagem recebida por: {member.name}", icon_url=member.avatar.url)
            try:
                await member.send(embed=embed)
                print(f'Mensagem enviada para {member.name}')
            except Exception as e:
                print(f'Não foi possível enviar mensagem para {member.name}: {e}')
    await interaction.response.send_message("Mensagens enviadas com sucesso!", ephemeral=True)
    await log_app_command(interaction, 'aviso')

@aviso.error
async def aviso_error(interaction: discord.Interaction, error):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("Você não tem permissão para usar este comando.", ephemeral=True)

# Função para registrar comandos tradicionais
async def log_command(ctx, command_name):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    embed = discord.Embed(
        title="Comando Executado",
        description=f"Comando: `{command_name}`\nHora: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        color=0xff0000
    )
    embed.set_footer(text=f"Usuário: {ctx.author}", icon_url=ctx.author.avatar.url)
    await log_channel.send(embed=embed)

# Função para registrar comandos de barra
async def log_app_command(interaction, command_name):
    log_channel = client.get_channel(LOG_CHANNEL_ID)
    embed = discord.Embed(
        title="Comando Executado",
        description=f"Comando: `{command_name}`\nHora: {datetime.datetime.now().strftime('%d/%m/%Y | %H:%M:%S')}",
        color=0xff0000
    )
    embed.set_footer(text=f"Executado por: {interaction.user}", icon_url=interaction.user.avatar.url)
    await log_channel.send(embed=embed)

#bot.loop.create_task(bot.start('MTMxNjk5NDcxNjc4NDM5NDI4MQ.GYN2Pg.D63v4wAuwQ-AAJ1JJbNTT7JJ8fbLSYmbb9eqUI'))
client.run('MTMxNjk5NDcxNjc4NDM5NDI4MQ.GYN2Pg.D63v4wAuwQ-AAJ1JJbNTT7JJ8fbLSYmbb9eqUI')
