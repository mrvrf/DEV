import discord
from discord.ext import commands, tasks
from discord import app_commands
import aiosqlite
import asyncio

DATABASE = "registro.db"

class RegistroCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.emote = "🍭"  # Default emoji (lollipop)
        self.role_id = 1361472124199637102  # Replace with the specific role ID
        self.bot.loop.create_task(self.load_emote())  # Load the emote from the database
        self.check_all_usernames_task.start()

    async def create_table(self):
        async with aiosqlite.connect(DATABASE) as db:
            # Create the registro table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS registro (
                    UserID TEXT PRIMARY KEY,
                    NomeFamilia TEXT NOT NULL,
                    NomePersonagem TEXT NOT NULL,
                    Classe TEXT NOT NULL
                )
            ''')
            # Create the emote table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS emote (
                    ID INTEGER PRIMARY KEY,
                    Emote TEXT NOT NULL
                )
            ''')
            # Ensure a default emote exists
            await db.execute('''
                INSERT OR IGNORE INTO emote (ID, Emote)
                VALUES (1, ?)
            ''', (self.emote,))
            await db.commit()

    async def load_emote(self):
        await self.create_table()
        async with aiosqlite.connect(DATABASE) as db:
            async with db.execute('SELECT Emote FROM emote WHERE ID = 1') as cursor:
                row = await cursor.fetchone()
                if row:
                    self.emote = row[0]

    async def check_all_usernames(self):
        """Check all users in the database and update their nicknames if necessary."""
        async with aiosqlite.connect(DATABASE) as db:
            async with db.execute("SELECT UserID, NomeFamilia, NomePersonagem FROM registro") as cursor:
                async for row in cursor:
                    user_id, nome_familia, nome_personagem = row
                    for guild in self.bot.guilds:  # Iterate through all guilds the bot is in
                        member = guild.get_member(int(user_id))
                        if not member:
                            print(f"Member with ID {user_id} not found in guild {guild.name}.")
                            continue

                        # Check if the member has the required role
                        role = discord.utils.get(member.roles, id=self.role_id)
                        if not role:
                            print(f"Member {member.display_name} does not have the required role in guild {guild.name}.")
                            continue

                        # Construct the expected nickname
                        expected_nickname = f"{self.emote} {nome_familia} | {nome_personagem}"
                        if member.nick != expected_nickname:
                            try:
                                await member.edit(nick=expected_nickname)
                                print(f"Nickname updated for {member.display_name} to {expected_nickname}.")
                            except discord.Forbidden:
                                print(f"Permission error: Could not update nickname for {member.display_name}.")
                            except Exception as e:
                                print(f"Unexpected error updating nickname for {member.display_name}: {e}")
                            await asyncio.sleep(2)

    @commands.Cog.listener()
    async def on_ready(self):
        """Event triggered when the bot is ready."""
        print(f"Bot is ready. Checking all usernames...")
        await self.check_all_usernames()

    @tasks.loop(minutes=1)
    async def check_all_usernames_task(self):
        """Task to periodically check all usernames."""
        print("Running periodic check for all usernames...")
        await self.check_all_usernames()

    @app_commands.command(name="registro", description="Registra informações no banco de dados")
    @app_commands.guild_only()
    async def registro(self, interaction: discord.Interaction, nome_familia: str, nome_personagem: str, classe: str):
        await self.create_table()
        async with aiosqlite.connect(DATABASE) as db:
            await db.execute('''
                INSERT OR REPLACE INTO registro (UserID, NomeFamilia, NomePersonagem, Classe)
                VALUES (?, ?, ?, ?)
            ''', (str(interaction.user.id), nome_familia, nome_personagem, classe))
            await db.commit()

        # Update the user's nickname
        new_nickname = f"{self.emote} {nome_familia} | {nome_personagem}"
        if interaction.guild:
            member = interaction.guild.get_member(interaction.user.id)
            if member:
                try:
                    await member.edit(nick=new_nickname)
                    await interaction.response.send_message(f"Registro salvo e nickname atualizado para: {new_nickname}", ephemeral=True)
                except discord.Forbidden:
                    await interaction.response.send_message("Não tenho permissão para alterar seu nickname.", ephemeral=True)
        else:
            await interaction.response.send_message("Registro salvo, mas não foi possível alterar o nickname.", ephemeral=True)

    @app_commands.command(name="setregemote", description="Define o emote usado no nickname")
    @app_commands.guild_only()
    async def setregemote(self, interaction: discord.Interaction, emote: str):
        # Validate the emote
        if len(emote) > 1 or not emote.strip():
            await interaction.response.send_message("Por favor, insira um único emoji válido.", ephemeral=True)
            return

        self.emote = emote  # Update the emote in memory

        # Save the new emote to the database
        async with aiosqlite.connect(DATABASE) as db:
            await db.execute('''
                INSERT OR REPLACE INTO emote (ID, Emote)
                VALUES (1, ?)
            ''', (emote,))
            await db.commit()

        await interaction.response.send_message(f"Emote atualizado para: {emote}", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(RegistroCommand(bot))