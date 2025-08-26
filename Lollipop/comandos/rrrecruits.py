import discord 
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
from discord.ui import Select, View

class_choices = [
    "Archer", "Berserker", "Corsair", "Dark Knight", "Drakania",
    "Guardian", "Hashashin", "Kunoichi", "Lahn", "Maehwa",
    "Musa", "Mystic", "Ninja", "Nova", "Ranger",
    "Sage", "Shai", "Sorceress", "Striker", "Tamer",
    "Valkyrie", "Warrior", "Witch", "Wizard", "Woosa"
]

class_mapping = {
    # Full names
    "Arqueiro": "Arqueiro", "Berserker": "Berserker", "Corsaria": "Corsaria",
    "Cavaleira das Trevas": "Cavaleira das Trevas", "Drakania": "Drakania",
    "Guardian": "Guardian", "Hashashin": "Hashashin",
    "Kunoichi": "Kunoichi", "Lahn": "Lahn",
    "Maehwa": "Maehwa", "Musah": "Musah",
    "Mistica": "Mistica", "Ninja": "Ninja", "Nova": "Nova",
    "Ranger": "Ranger", "Sage": "Sage", "Shai": "Shai",
    "Feiticeira": "Feiticeira", "Striker": "Striker",
    "Tamer": "Tamer", "Valquiria": "Valquiria",
    "Warrior": "Warrior", "Bruxa": "Bruxa", "Mago": "Mago",
    "Wusa": "Wusa", "Megu": "Megu", "Dosa": "Dosa", "Erudita": "Erudita",
    "Deadeye": "Deadeye", "Wukong": "Wukong"
}

class Recruit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.setup_database()
        self.guildas = {
            929344073221935104: "Allyance",
            935733958266716200: "Grand_Order",
            1206381250064158740: "Manifest",
        }
        self.raids = {
            942684778510045205: "Elefanteiro",
            978853483782492180: "Flanco",
            1210354501870166077: "Raid 1",
            1210354582048473088: "Raid 2",
            1210354616840093796: "Raid 3",
            1210354659378860083: "Raid 4",
            959267503475949578: "Defesa",
        }

    def setup_database(self):
        with sqlite3.connect('profiles.db') as conn:
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    user_id INTEGER PRIMARY KEY,
                    family_name TEXT,
                    character_name TEXT,
                    main_class TEXT,
                    linked_class TEXT,
                    ap INTEGER,
                    aap INTEGER,
                    dp INTEGER,                    
                    created_at TIMESTAMP,
                    link_gear TEXT
                )
            ''')
            conn.commit()

    async def get_guildas(self, member):
        for role in member.roles:
            if role.id in self.guildas:
                return self.guildas[role.id]
        return None
    
    async def get_raids(self, member):
        try:
            # Get member's actual roles
            print(f"{datetime.now()} | Verificando cargos para usuario: {member.display_name}")
            member_role_ids = [role.id for role in member.roles]
            
            # Check if member has any raid roles
            for role_id, raid_name in self.raids.items():
                if role_id in member_role_ids:
                    print(f"Encontrado cargo: {raid_name} para o membro {member.display_name}")
                    return raid_name
                    
            print(f"No raid role found for member {member.display_name}")
            return None
            
        except Exception as e:
            print(f"Error in get_raids: {e}")
            return None

    def preserve_caps(self, text: str) -> str:
        words = text.split()
        return ' '.join(word[0].upper() + word[1:] if word else '' for word in words)

    @app_commands.command(name="registro", description="Registra seu perfil")
    @app_commands.guild_only()
    @app_commands.checks.has_role(1392610552794189866)  # Replace with your role ID
    @app_commands.describe(
        nome_familia="Nome de Família",
        nome_personagem="Nome do Personagem",
        classe_main="Classe Principal",
        classe_linkada="Classe Secundária",
        ap="Poder de ataque com gear pvp",
        aap="Poder de ataque awakening com gear pvp",
        dp="Poder de defesa",
        gear_link="Link do Gear (opcional)"
    )
    async def registro(self, interaction: discord.Interaction, 
                      nome_familia: str, 
                      nome_personagem: str,
                      classe_main: str,
                      classe_linkada: str,
                      ap: int,
                      aap: int,
                      dp: int,
                      gear_link: str = None):
        try:
            await interaction.response.defer(ephemeral=True)

            nome_familia = self.preserve_caps(nome_familia)
            nome_personagem = self.preserve_caps(nome_personagem)
            
            # Validate and convert class names
            classe_main = classe_main.title()
            classe_linkada = classe_linkada.title()
            
            if classe_main not in class_mapping:
                invalido_embed = discord.Embed(
                    title="Classe Principal Inválida",
                    description=f"**Classe principal inválida. Classes disponíveis:**\n{', '.join(sorted(set(class_mapping.values())))}",
                    color=0xFF0000
                )
                await interaction.followup.send(embed=invalido_embed, ephemeral=True)
                #await interaction.followup.send(f"Classe principal inválida. Classes disponíveis: {', '.join(sorted(set(class_mapping.values())))}", ephemeral=True)
                return
                
            if classe_linkada not in class_mapping:
                invalido_embed = discord.Embed(
                    title="Classe Secundaria Inválida",
                    description=f"**Classe secundaria inválida. Classes disponíveis:**\n{', '.join(sorted(set(class_mapping.values())))}",
                    color=0xFF0000
                )
                await interaction.followup.send(embed=invalido_embed, ephemeral=True)
                #await interaction.followup.send(f"Classe linkada inválida. Classes disponíveis: {', '.join(sorted(set(class_mapping.values())))}", ephemeral=True)
                return
            
            # Convert to full names
            main_class = class_mapping[classe_main]
            linked_class = class_mapping[classe_linkada]
            
            with sqlite3.connect('profiles.db') as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT OR REPLACE INTO profiles 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    interaction.user.id,
                    nome_familia,
                    nome_personagem,
                    main_class,
                    linked_class,
                    ap,
                    aap,
                    dp,                    
                    datetime.now(),
                    gear_link if gear_link else None
                ))
                conn.commit()

            try:
                role = interaction.guild.get_role(1395196503261446146)
                if role:
                    await interaction.user.add_roles(role)
                    print(f"{datetime.now()}: Cargo {role.name} adicionado a {interaction.user.display_name}")
            except Exception as e:
                print(f"{datetime.now()}: Erro ao adicionar cargo: {e}")

            embed = discord.Embed(
                title="✅ Registro Concluído",
                description="Seu perfil foi registrado com sucesso!\nUtilize /perfil para visualizar seu perfil.",
                color=0x00FF00
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

            embed_log = discord.Embed(
                title="**Novo Registro**",
                description=f"**Usuário:** {interaction.user.mention}\n**Família:** {nome_familia}\n**Personagem:** {nome_personagem}\n**Classe Main:** {main_class}\n**Classe Linkada:** {linked_class}\n**AP:** {ap}\n**AAP:** {aap}\n**DP:** {dp}\n**Link Gear:** {gear_link if gear_link else 'Nenhum link'}",
                color=0xFFFFFF,
                timestamp=datetime.now()
            )

            

            embed_log.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            log_channel = self.bot.get_channel(1318400984531210281)  # Replace with your log channel ID
            if log_channel:
                await log_channel.send(embed=embed_log)


            print(f"{datetime.now()}: Registro de {interaction.user.display_name} concluído com sucesso.")

        except Exception as e:
            print(f"Error in registro: {e}")
            await interaction.followup.send("Erro ao registrar perfil.", ephemeral=True)

    @app_commands.command(name="perfil", description="Mostra seu perfil")
    @app_commands.checks.has_role(1361472124199637102)
    @app_commands.guild_only()
    async def perfil(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)

            with sqlite3.connect('profiles.db') as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM profiles WHERE user_id = ?', (interaction.user.id,))
                data = c.fetchone()

            if not data:
                await interaction.followup.send(
                    "Perfil não encontrado. Use /registro para criar seu perfil.",
                    ephemeral=False
                )
                return
            
            
            role_guilda = await self.get_guildas(interaction.user)
            role_raid = await self.get_raids(interaction.user)

            aps = data[5] + data[6]  # AP + AAP
            ap2 = aps / 2  # AP + AAP * 2
            gs = int(ap2 + data[7])  # APS + DP

            embed = discord.Embed(
                title=f"{interaction.user.display_name}",
                color=0x3d85c6,
                timestamp=datetime.now()
            )
            
            embed.add_field(name="📄Família", value=data[1], inline=True)
            embed.add_field(name="📄Personagem", value=data[2], inline=True)
            embed.add_field(name="🔰Guilda", value=role_guilda if role_guilda else "Sem guilda⚠️", inline=True)
            #embed.add_field(name="\u200b", value="\u200b", inline=True)
            embed.add_field(name="🚩Raid", value=role_raid if role_raid else "Sem raid⚠️", inline=True)
            embed.add_field(name="🆑asse 1", value=data[3], inline=True)
            embed.add_field(name="🆑asse 2", value=data[4], inline=True)
            #embed.add_field(name="\u200b", value="\u200b", inline=True)
            embed.add_field(name="🗡️AP Pre/Succ", value=data[5], inline=True)
            embed.add_field(name="⚔️AP Awakening", value=data[6], inline=True)
            embed.add_field(name="🛡️DP", value=data[7], inline=True)
            embed.add_field(name="🏆Gearscore", value=f"{gs}", inline=True)
            #embed.add_field(name="📎Link Gear", value=(data[9] if data[9] else "⚠️Nenhum link"), inline=True)
            embed.add_field(name="📎Link Gear", value=f"[Clique aqui]({data[9]})" if data[9] and data[9].strip() else "Nenhum link", inline=True)
            embed.add_field(name="📅Criado em", value=(data[8])[:16], inline=True)
            
            embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            embed.set_footer(text=f"{data[3]} {gs}gs")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            print(f"Perfil de {interaction.user.display_name} mostrado com sucesso.")

        except Exception as e:
            print(f"Error in perfil: {e}")
            await interaction.followup.send("Erro ao mostrar perfil.", ephemeral=True)

    class RaidSelectView(View):
        def __init__(self, bot, target_user):
            super().__init__()
            self.bot = bot
            self.target_user = target_user
            
            # Create raid selection menu
            select = Select(
                placeholder="Selecionar Raid",
                options=[
                    discord.SelectOption(label=raid_name, value=str(raid_id))
                    for raid_id, raid_name in bot.get_cog('Recruit').raids.items()
                ]
            )
            select.callback = self.raid_callback
            self.add_item(select)

        async def raid_callback(self, interaction: discord.Interaction):
            try:
                # Get the selected raid role ID
                new_role_id = int(interaction.data['values'][0])
                guild = interaction.guild
                member = guild.get_member(self.target_user.id)
                
                # Remove existing raid roles
                for raid_id in self.bot.get_cog('Recruit').raids.keys():
                    role = guild.get_role(raid_id)
                    if role and role in member.roles:
                        await member.remove_roles(role)
                
                # Add new raid role
                new_role = guild.get_role(new_role_id)
                if new_role:
                    await member.add_roles(new_role)
                    await interaction.response.send_message(
                        f"Raid atualizada para {self.bot.get_cog('Recruit').raids[new_role_id]}",
                        ephemeral=True
                    )
                
            except Exception as e:
                print(f"Error in raid selection: {e}")
                await interaction.response.send_message("Erro ao atualizar raid.", ephemeral=True)

    @app_commands.command(name="pre", description="Mostra o perfil de outro usuário")
    @app_commands.describe(user="Usuário para verificar o perfil")
    @app_commands.guild_only()
    @app_commands.checks.has_role(1361472124199637102)
    async def pre(self, interaction: discord.Interaction, user: discord.User):
        try:
            await interaction.response.defer(ephemeral=True)

            with sqlite3.connect('profiles.db') as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM profiles WHERE user_id = ?', (user.id,))
                data = c.fetchone()

            if not data:
                await interaction.followup.send(
                    f"Perfil não encontrado para {user.display_name}.",
                    ephemeral=True
                )
                return

            role_guilda = await self.get_guildas(user)
            role_raid = await self.get_raids(user)

            aps = data[5] + data[6]  # AP + AAP
            ap2 = aps / 2  # AP + AAP * 2
            gs = int(ap2 + data[7])  # APS + DP

            embed = discord.Embed(
                title=f"Perfil de {user.display_name}",
                color=0x3d85c6,
                timestamp=datetime.now()
            )
            
            embed.add_field(name="📄Família", value=data[1], inline=True)
            embed.add_field(name="📄Personagem", value=data[2], inline=True)
            embed.add_field(name="🔰Guilda", value=role_guilda if role_guilda else "Sem guilda⚠️", inline=True)
            embed.add_field(name="🚩Raid", value=role_raid if role_raid else "Sem raid⚠️", inline=True)
            embed.add_field(name="🆑asse 1", value=data[3], inline=True)
            embed.add_field(name="🆑asse 2", value=data[4], inline=True)
            embed.add_field(name="🗡️AP Pre/Succ", value=data[5], inline=True)
            embed.add_field(name="⚔️AP Awakening", value=data[6], inline=True)
            embed.add_field(name="🛡️DP", value=data[7], inline=True)
            embed.add_field(name="🏆Gearscore", value=f"{gs}", inline=True)
            embed.add_field(name="📎Link Gear", value=data[9] if data[9] and data[9].strip() else "Nenhum link", inline=True)
            embed.add_field(name="📅Criado em", value=(data[8])[:16], inline=True)
            
            embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
            embed.set_footer(text=f"{data[3]} {gs}gs")
            
            # Create and add the raid selection menu
            view = Recruit.RaidSelectView(self.bot, user)
            await interaction.followup.send(embed=embed, view=view, ephemeral=True)
            print(f"Perfil de {user.display_name} mostrado com sucesso.")

        except Exception as e:
            print(f"Error in pre: {e}")
            await interaction.followup.send("Erro ao mostrar perfil.", ephemeral=True)
    

async def setup(bot):
    await bot.add_cog(Recruit(bot))