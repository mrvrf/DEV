import discord
from discord.ext import commands
from discord import app_commands
import json
import os

class Canute(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.prefixes = self.load_prefixes()
        self.profiles = self.load_profiles()

    def load_prefixes(self):
        if os.path.exists('prefixes.json'):
            with open('prefixes.json', 'r') as f:
                return json.load(f)
        return {}

    def save_prefixes(self):
        with open('prefixes.json', 'w') as f:
            json.dump(self.prefixes, f)

    def load_profiles(self):
        if os.path.exists('profiles.json'):
            with open('profiles.json', 'r') as f:
                return json.load(f)
        return {}

    def save_profiles(self):
        with open('profiles.json', 'w') as f:
            json.dump(self.profiles, f)

    @app_commands.command(name="setprefix", description="Set a prefix for a role and update display names.")
    @app_commands.describe(role="Role to set the prefix for", prefix="Prefix to set")
    @app_commands.checks.has_permissions(administrator=True)
    async def setprefix(self, interaction: discord.Interaction, role: discord.Role, prefix: str):
        guild_id = str(interaction.guild.id)
        role_id = str(role.id)

        if guild_id not in self.prefixes:
            self.prefixes[guild_id] = {}

        self.prefixes[guild_id][role_id] = prefix
        self.save_prefixes()

        await interaction.response.send_message(f"Prefixo `{prefix}` definido para o cargo `{role.name}`.", ephemeral=True)

        for member in role.members:
            if not member.bot:
                new_nickname = f"{prefix} {member.display_name}"
                try:
                    await member.edit(nick=new_nickname)
                except discord.Forbidden:
                    await interaction.followup.send(f"Não foi possível alterar o apelido de {member.display_name} devido a permissões insuficientes.", ephemeral=True)

    @app_commands.command(name="removeprefix", description="Remove the prefix for a role and update display names.")
    @app_commands.describe(role="Role to remove the prefix from")
    @app_commands.checks.has_permissions(administrator=True)
    async def removeprefix(self, interaction: discord.Interaction, role: discord.Role):
        guild_id = str(interaction.guild.id)
        role_id = str(role.id)

        if guild_id in self.prefixes and role_id in self.prefixes[guild_id]:
            prefix = self.prefixes[guild_id][role_id]
            del self.prefixes[guild_id][role_id]
            self.save_prefixes()

            await interaction.response.send_message(f"Prefixo removido para o cargo `{role.name}`.", ephemeral=True)

            for member in role.members:
                if not member.bot:
                    original_nickname = member.display_name.replace(prefix, "").strip()
                    try:
                        await member.edit(nick=original_nickname)
                    except discord.Forbidden:
                        await interaction.followup.send(f"Não foi possível alterar o apelido de {member.display_name} devido a permissões insuficientes.", ephemeral=True)
        else:
            await interaction.response.send_message(f"Não há prefixo definido para o cargo `{role.name}`.", ephemeral=True)

    @app_commands.command(name="update", description="Registrar novo perfil ou atualizar perfil existente")
    @app_commands.describe(family_name="Nome de Familia", character_name="Nome de Personagem", classe="Classe", ap="AP", ap_awak="AP Awak", dp="DP")
    async def mem_update(self, interaction: discord.Interaction, family_name: str, character_name: str, classe: str, ap: int, ap_awak: int, dp: int):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)

        if guild_id not in self.profiles:
            self.profiles[guild_id] = {}

        # Check for unique family and character names
        for user_profile in self.profiles[guild_id].values():
            if user_profile['family_name'] == family_name and user_profile['user_id'] != user_id:
                await interaction.response.send_message("Nome de Familia já está em uso.", ephemeral=True)
                return
            if user_profile['character_name'] == character_name and user_profile['user_id'] != user_id:
                await interaction.response.send_message("Nome de Personagem já está em uso.", ephemeral=True)
                return

        self.profiles[guild_id][user_id] = {
            'user_id': user_id,
            'family_name': family_name,
            'character_name': character_name,
            'classe': classe,
            'ap': ap,
            'ap_awak': ap_awak,
            'dp': dp
        }
        self.save_profiles()

        await interaction.response.send_message("Perfil atualizado com sucesso.", ephemeral=True)

    @app_commands.command(name="me", description="Mostra seu perfil registrado")
    async def mem_me(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)
        user_id = str(interaction.user.id)
        gearscore = int((self.profiles[guild_id][user_id]['ap'] + self.profiles[guild_id][user_id]['ap_awak']) / 2) + self.profiles[guild_id][user_id]['dp']        

        if guild_id in self.profiles and user_id in self.profiles[guild_id]:
            profile = self.profiles[guild_id][user_id]
            embed = discord.Embed(title="Seu Perfil", color=discord.Color.green() if gearscore >= 740 else discord.Color.red())
            embed.set_thumbnail(url=interaction.user.avatar.url)
            embed.add_field(name="Nome de Familia", value=profile['family_name'], inline=True)
            embed.add_field(name="Nome de Personagem", value=profile['character_name'], inline=True)
            embed.add_field(name="AP", value=profile['ap'], inline=False)
            embed.add_field(name="AP Awak", value=profile['ap_awak'], inline=False)
            embed.add_field(name="DP", value=profile['dp'], inline=False)
            embed.add_field(name="Classe", value=profile['classe'], inline=True)
            embed.add_field(name="Gear Score", value=f"{gearscore}gs", inline=True)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("Você não tem um perfil registrado.", ephemeral=True)

    @app_commands.command(name="info", description="Mostra o perfil do membro")
    @app_commands.describe(user="Membro para mostrar o perfil")
    async def mem_info(self, interaction: discord.Interaction, user: discord.User):
        guild_id = str(interaction.guild.id)
        user_id = str(user.id)
        gearscore = int((self.profiles[guild_id][user_id]['ap'] + self.profiles[guild_id][user_id]['ap_awak']) / 2) + self.profiles[guild_id][user_id]['dp']

        if guild_id in self.profiles and user_id in self.profiles[guild_id]:
            profile = self.profiles[guild_id][user_id]
            embed = discord.Embed(title=f"Perfil de {user.display_name}", color=discord.Color.green() if gearscore >= 740 else discord.Color.red())
            embed.set_thumbnail(url=user.avatar.url)
            embed.add_field(name="Nome de Familia", value=profile['family_name'], inline=False)
            embed.add_field(name="Nome de Personagem", value=profile['character_name'], inline=False)
            embed.add_field(name="Classe", value=profile['classe'], inline=False)
            embed.add_field(name="AP", value=profile['ap'], inline=False)
            embed.add_field(name="AP Awak", value=profile['ap_awak'], inline=False)
            embed.add_field(name="DP", value=profile['dp'], inline=False)
            embed.add_field(name="Gear Score", value=f"{gearscore}gs", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("Este usuário não tem um perfil registrado.", ephemeral=True)

    @app_commands.command(name="list", description="Lista todos os membros registrados")
    async def mem_list(self, interaction: discord.Interaction):
        guild_id = str(interaction.guild.id)

        if guild_id in self.profiles:
            embed = discord.Embed(title="Membros Registrados")
            for profile in self.profiles[guild_id].values():
                embed.add_field(
                    name=profile['family_name'],
                    value=f"AP: {profile['ap']} | AAP: {profile['ap_awak']} | DP: {profile['dp']} | Classe: {profile['classe']}",
                    inline=False
                )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message("Não há membros registrados neste servidor.", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            added_roles = [role for role in after.roles if role not in before.roles]
            for role in added_roles:
                guild_id = str(after.guild.id)
                role_id = str(role.id)
                if guild_id in self.prefixes and role_id in self.prefixes[guild_id]:
                    prefix = self.prefixes[guild_id][role_id]
                    new_nickname = f"{prefix} {after.display_name}"
                    try:
                        await after.edit(nick=new_nickname)
                    except discord.Forbidden:
                        pass  # Handle insufficient permissions

async def setup(bot: commands.Bot):
    cog = Canute(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(app_commands.Group(name="mem", description="Grupo Mem"))
    bot.tree.get_command("mem").add_command(cog.mem_update)
    bot.tree.get_command("mem").add_command(cog.mem_me)
    bot.tree.get_command("mem").add_command(cog.mem_info)
    bot.tree.get_command("mem").add_command(cog.mem_list)