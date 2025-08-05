import discord
from discord.ext import commands, tasks
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import sys
import asyncio
from datetime import datetime
import threading
import aiosqlite
from comandos.db import initialize_db, upsert_player

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.presences = True
        intents.voice_states = True
        super().__init__(command_prefix="_", intents=intents)
        self.initial_extensions = [
            #'comandos.setnode',
            #'comandos.setsiege', 
            'comandos.aviso', 
            #'comandos.ping',
            'comandos.confere',
            'comandos.confere2',
            #'comandos.lista',
            #'comandos.ajuda',
            'comandos.teste',
            #'comandos.alert',
            'comandos.pmensagem',
            #'comandos.limpa',
            #'comandos.embedT',
            #'comandos.mover',
            #'comandos.gvg',
            #'comandos.guild_profile',
            'comandos.vodreview',
            #'comandos.alone',
            #'comandos.online',
            #'comandos.presenca',
            'comandos.control',
            'comandos.self',
            #'comandos.cobrar',
            #'comandos.check_confere',
            'comandos.bot_log',
            'comandos.recruit'
            #'comandos.teste_presenca'
        ]
        self.role_id = 1361472124199637102 # ID do cargo que contém os jogadores
        self.guild_id = 929343217915297812
    
    async def setup_hook(self):
        await initialize_db()
        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
                print(f'{datetime.now().strftime("%d/%m/%Y | %H:%M")} Extensão carregada: {extension} ')
            except Exception as e:
                print(f'Erro ao carregar extensão {extension}: {e}')
        await self.tree.sync()  
        print("Global slash commands synced.")
        #self.update_activity.start()  
        self.update_players.start()  

#    @tasks.loop(minutes=300)  
#    async def update_activity(self):
#        guild = self.get_guild(self.guild_id)
#        if guild:
#            role = guild.get_role(self.role_id)
#            if role:
#                player_count = len(role.members)
#                activity = discord.Activity(type=discord.ActivityType.watching, name=f"{player_count} Players")
#                print(f"Updating activity to {activity}")
#                await self.change_presence(activity=activity)

#    @update_activity.before_loop
#    async def before_update_activity(self):
#        await self.wait_until_ready()

    @tasks.loop(hours=24)
    async def update_players(self):
        guild = self.get_guild(self.guild_id)
        if guild:
            role = guild.get_role(self.role_id)
            if role:
                player_count = len(role.members)
                activity = discord.Activity(type=discord.ActivityType.watching, name=f"{player_count} Players")
                print(f"Updating activity to {activity}")
                await self.change_presence(activity=activity)
                for member in role.members:
                    #print(f"Atualizando jogador: {member.display_name}")
                    await upsert_player(str(member.id), member.name, member.display_name)
                    
                    
        quant_att = len(role.members)
        log_channel = self.get_channel(1318401148151009391)
        await log_channel.send(f"{quant_att} jogadores atualizados.\nAtividade atualizada - {player_count} Players | Cargo usado: {role.name}")


    @update_players.before_loop
    async def before_update_players(self):
        await self.wait_until_ready()

intents = discord.Intents.default()
intents.members = True  # Ensure the bot has the members intent
intents.voice_states = True  # Ensure the bot has the voice states intent

bot = MyBot(command_prefix="!", intents=intents)

class RedirectOutput:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.config(state=tk.NORMAL)
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)
        self.text_widget.config(state=tk.DISABLED)

    def flush(self):
        pass

@bot.event
async def on_ready():
    print(f'Bot {bot.user} está online!')
    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(type=discord.ActivityType.watching, name="Lollipop 🚀")
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

def run_bot():
    asyncio.run(bot.start("MTMyMTYxMjI5NDUwMDkwOTEwNg.GvkCUI.VTMaT-j95TqEA8zYFHTpyIfhnHtNRVfcVyZ32k"))

def create_gui():
    root = tk.Tk()
    root.title("Lollipop")
    root.geometry("800x800")

    text_widget = ScrolledText(root, state='disabled', wrap='word')
    text_widget.pack(expand=True, fill='both')

    sys.stdout = RedirectOutput(text_widget)
    sys.stderr = RedirectOutput(text_widget)

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    root.mainloop()

if __name__ == "__main__":
    create_gui()