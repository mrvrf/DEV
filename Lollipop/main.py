import discord
from discord.ext import commands
from datetime import datetime

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="_", intents=intents)
        self.initial_extensions = [
            'comandos.setnode',
            'comandos.setsiege', 
            'comandos.aviso', 
            'comandos.ping',
            'comandos.confere',
            'comandos.lista',
            'comandos.ajuda',
            'comandos.teste',
            'comandos.alert',
            'comandos.pmensagem',
            'comandos.limpa',
            #'comandos.embedT',
            'comandos.mover',
            'comandos.gvg',
            #'comandos.canute'
            'comandos.alone'
        ]
    
    async def setup_hook(self):
        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
                print(f'Extensão carregada: {extension}')
            except Exception as e:
                print(f'Erro ao carregar extensão {extension}: {e}')
        await self.tree.sync()  # Syncing globally
        print("Global slash commands synced.")

bot = MyBot()

@bot.event
async def on_ready():
    print(f'Bot {bot.user} está online!')
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name="Bagres grindando 🐟")
    )
    print("Comandos carregados:")
    for command in bot.tree.get_commands():
        print(command.name)

    log_embed = discord.Embed(
            title=f"**Online**",
            description=f"Bot online!\n{len(bot.tree.get_commands())} comandos carregados.",
            color=0x38761D
        )
    log_embed.set_footer(text=f"{datetime.now().strftime('%d/%m/%Y | %H:%M')}")

    log_channel = bot.get_channel(1318401148151009391)
    await log_channel.send(embed=log_embed)

    user_id = 268471873073840128
    user = await bot.fetch_user(user_id)
    if user:
        try:
            await user.send("Bot online!")
            print(f"BOT ONLINE - Mensagem enviada para {user.name} {datetime.now().strftime('%d/%m/%Y | %H:%M')}")
        except discord.Forbidden:
            print(f"Não foi possível enviar mensagem para {user.name}")

@bot.check
async def globally_block_dms(ctx):
    if ctx.guild is None:
        await ctx.send("Erro!")
        return False
    return True

@bot.check
async def globally_block_dms(interaction: discord.Interaction):
    if interaction.guild is None:
        await interaction.response.send_message("Erro!", ephemeral=True)
        return False
    return True

bot.run('MTMyMTYxMjI5NDUwMDkwOTEwNg.GvkCUI.VTMaT-j95TqEA8zYFHTpyIfhnHtNRVfcVyZ32k')