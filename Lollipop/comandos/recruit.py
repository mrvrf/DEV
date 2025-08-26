import discord 
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
from discord.ui import Select, View, Button

class_mapping = {
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
            1244387844961603766: "Bandeira",
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
                    ap INTEGER,
                    aap INTEGER,
                    dp INTEGER,                    
                    created_at TIMESTAMP,
                    link_gear TEXT,
                    last_updated TIMESTAMP
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
        
    async def get_lollipop_average(self):
        try:
            with sqlite3.connect('profiles.db') as conn:
                c = conn.cursor()
                lollipop_role_id = 1361472124199637102  # ID do cargo Lollipop
                guild = self.bot.get_guild(929343217915297812)  # ID do servidor
                role = guild.get_role(lollipop_role_id)

                member_ids = [member.id for member in role.members]
                placeholders = ','.join('?' * len(member_ids))

                c.execute(f'''
                    SELECT AVG((ap+aap) / 2 + dp) as avg_gs
                    FROM profiles
                    WHERE user_id IN ({placeholders})
                ''', member_ids)

                result = c.fetchone()
                return result[0] if result and result[0] else 0
        except Exception as e:
            print(f"Error calculating get_lollipop_average: {e}")
            return 0
        
    async def get_guild_average(self, user):
        try:
            with sqlite3.connect('profiles.db') as conn:
                c = conn.cursor()
                guild = self.bot.get_guild(929343217915297812)  # ID do servidor

                guild_role_id = None
                #member_roles = set(role.id for role in guild.get_member(self.bot.user.id).roles)

                for role_id in self.guildas.keys():
                    if discord.utils.get(user.roles, id=role_id):
                        guild_role_id = role_id
                        break

                if not guild_role_id:
                    return None
                
                guild_members = [member.id for member in guild.get_role(guild_role_id).members]

                if not guild_members:
                    return None
                
                placeholders = ','.join('?' * len(guild_members))
                c.execute(f'''
                    SELECT AVG((ap+aap) / 2 + dp) as avg_gs
                    FROM profiles
                    WHERE user_id IN ({placeholders})
                ''', guild_members)

                result = c.fetchone()
                return result[0] if result and result[0] else None
            
        except Exception as e:
            print(f"Error calculating get_guild_average: {e}")
            return None
        
    async def get_class_average(self, class_name):
        try:
            with sqlite3.connect('profiles.db') as conn:
                c = conn.cursor()
                registered_role_id = 1395196503261446146  # ID do cargo Registrado
                guild = self.bot.get_guild(929343217915297812)  # ID do servidor
                role = guild.get_role(registered_role_id)

                member_ids = [member.id for member in role.members]
                placeholders = ','.join('?' * len(member_ids))

                c.execute(f'''
                    SELECT AVG((ap+aap) / 2 + dp) as avg_gs
                    FROM profiles
                    WHERE user_id IN ({placeholders}) AND main_class = ?
                ''', member_ids + [class_name])

                result = c.fetchone()
                return result[0] if result and result[0] else None
        except Exception as e:
            print(f"Error calculating get_class_average: {e}")
            return None
        

    def preserve_caps(self, text: str) -> str:
        words = text.split()
        return ' '.join(word[0].upper() + word[1:] if word else '' for word in words)
    
    class RegistrationView(View):
        def __init__(self, user):
            super().__init__(timeout=None)
            self.user = user

            register_button = discord.ui.Button(
                label="Registrar",
                style=discord.ButtonStyle.primary,
                custom_id="register_button"
            )
            register_button.callback = self.register_callback
            self.add_item(register_button)

        async def register_callback(self, interaction: discord.Interaction):
            approval_channel = interaction.guild.get_channel(1347342392952357016)  # Replace with your approval channel ID

            embed = discord.Embed(
                title="Solicitação de Registro",
                description=f"Membro: {self.user.mention}\nID: {self.user.id}",
                color=0x3d85c6,
                timestamp=datetime.now()
            )
            embed.set_thumbnail(url=self.user.avatar.url if self.user.avatar else self.user.default_avatar.url)

            view = Recruit.ApprovalView(self.user)
            await approval_channel.send(embed=embed, view=view)

            await interaction.response.send_message("Solicitação de registro enviada para aprovação.", ephemeral=True)

    class ApprovalView(View):
        def __init__(self, target_user):
            super().__init__(timeout=None)
            self.target_user = target_user

            approve_button = Button(
                label="Aprovar",
                style=discord.ButtonStyle.green,
                custom_id="approve_button"
            )
            approve_button.callback = self.approve_callback
            self.add_item(approve_button)

            disapprove_button = Button(
                label="Reprovar",
                style=discord.ButtonStyle.red,
                custom_id="disapprove_button"
            )
            disapprove_button.callback = self.disapprove_callback
            self.add_item(disapprove_button)

        async def approve_callback(self, interaction: discord.Interaction):
            try:
                role = interaction.guild.get_role(1392610552794189866)  # Replace with your role ID
                member = interaction.guild.get_member(self.target_user.id)
                if role and member:
                    await member.add_roles(role, reason="Registro aprovado")

                try:
                    await self.target_user.send(
                        "Sua solicitação de registro foi aprovada.\n"
                        "Use o comando /registro para iniciar seu registro."
                    )
                except discord.Forbidden:
                    print(f"Não foi possível enviar mensagem direta para {self.target_user.name}.")

                for child in self.children:
                    child.disabled = True
                await interaction.message.edit(view=self)

                await interaction.response.send_message(f"Registro aprovado para {self.target_user.mention}", ephemeral=True)

            except Exception as e:
                print(f"Error in approve_callback: {e}")
                await interaction.response.send_message("Erro ao aprovar o registro.", ephemeral=True)

        async def disapprove_callback(self, interaction: discord.Interaction):
            try:
                try:
                    await self.target_user.send(
                        "Sua solicitação de registro foi negada.\n"
                    )
                except discord.Forbidden:
                    print(f"Não foi possível enviar mensagem direta para {self.target_user.name}.")

                for child in self.children:
                    child.disabled = True
                await interaction.message.edit(view=self)

                await interaction.response.send_message(f"Registro negado para {self.target_user.mention}", ephemeral=True)

            except Exception as e:
                print(f"Error in disapprove_callback: {e}")
                await interaction.response.send_message("Erro ao negar o registro.", ephemeral=True)

    @app_commands.command(name="registro", description="Registra seu perfil")
    @app_commands.guild_only()
    @app_commands.checks.has_role(1392610552794189866)  # Replace with your role ID
    @app_commands.describe(
        nome_familia="Nome de Família",
        nome_personagem="Nome do Personagem",
        classe_pvp="Classe PvP",
        ap="Poder de ataque com gear pvp",
        aap="Poder de ataque awakening com gear pvp",
        dp="Poder de defesa",
        gear_link="Link do Gear (imgur ou link de imagem)"
    )
    async def registro(self, interaction: discord.Interaction, 
                      nome_familia: str, 
                      nome_personagem: str,
                      classe_pvp: str,
                      ap: int,
                      aap: int,
                      dp: int,
                      gear_link: str):
        try:
            await interaction.response.defer(ephemeral=True)

            log_embed = discord.Embed(
            title="**Comando Executado**",
            description=f"**Comando:** */registro*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
            color=0xFFFFFF
            )
            log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

            log_channel = interaction.guild.get_channel(1318401148151009391)
            await log_channel.send(embed=log_embed)

            nome_familia = self.preserve_caps(nome_familia)
            nome_personagem = self.preserve_caps(nome_personagem)
            
            # Validate and convert class names
            classe_pvp = classe_pvp.title()
            
            if classe_pvp not in class_mapping:
                invalido_embed = discord.Embed(
                    title="Classe Principal Inválida",
                    description=f"**Classe principal inválida. Classes disponíveis:**\n{', '.join(sorted(set(class_mapping.values())))}",
                    color=0xFF0000
                )
                await interaction.followup.send(embed=invalido_embed, ephemeral=True)
                #await interaction.followup.send(f"Classe principal inválida. Classes disponíveis: {', '.join(sorted(set(class_mapping.values())))}", ephemeral=True)
                return
            
            # Convert to full names
            main_class = class_mapping[classe_pvp]
            
            with sqlite3.connect('profiles.db') as conn:
                c = conn.cursor()
                c.execute('''
                    INSERT OR REPLACE INTO profiles
                    (user_id, family_name, character_name, main_class,
                     ap, aap, dp, created_at, link_gear, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    interaction.user.id,
                    nome_familia,
                    nome_personagem,
                    main_class,
                    ap,
                    aap,
                    dp,                    
                    datetime.now(),
                    gear_link if gear_link else None,
                    datetime.now()
                ))
                conn.commit()

            try:
                role = interaction.guild.get_role(1395196503261446146)
                lollipop = interaction.guild.get_role(1361472124199637102)
                agrole = interaction.guild.get_role(1392610552794189866)
                if role:
                    await interaction.user.add_roles(role, reason="Registro de perfil")
                    await interaction.user.add_roles(lollipop, reason="Registro de perfil")
                    await interaction.user.remove_roles(agrole, reason="Registro de perfil")
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
                description=f"**Usuário:** {interaction.user.mention}\n**Família:** {nome_familia}\n**Personagem:** {nome_personagem}\n**Classe Main:** {main_class}\n**AP:** {ap}\n**AAP:** {aap}\n**DP:** {dp}\n**Link Gear:** {gear_link if gear_link else 'Nenhum link'}",
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
        
    @registro.error
    async def registro_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingRole):
            try:
                with sqlite3.connect('profiles.db') as conn:
                    c = conn.cursor()
                    c.execute('SELECT user_id FROM profiles WHERE user_id = ?', (interaction.user.id,))
                    exists = c.fetchone()

                if exists:
                    await interaction.response.send_message(
                        "Você já está registrado. Use **/atualizar** para atualizar seu perfil.",
                        ephemeral=True
                    )
                else:
                    view = Recruit.RegistrationView(interaction.user)
                    await interaction.response.send_message(
                    "Você não tem permissão para usar este comando.\n\n" \
                    "Caso já esteja registrado por favor utilize **/atualizar** para atualizar seu /perfil !\n" \
                    "Se você não está registrado e deseja registrar, clique no botão.", view=view, ephemeral=True)
            except Exception as e:
                print(f"Error in registro_error: {e}")
                await interaction.response.send_message("Erro ao verificar registro.", ephemeral=True)                
        else:
            print(f'Error in teste command: {error}')

    @app_commands.command(name="atualizar", description="Atualiza seu perfil")
    @app_commands.guild_only()
    @app_commands.checks.has_role(1395196503261446146)  # Replace with your role ID
    @app_commands.describe(
        nome_familia="Nome de Família",
        nome_personagem="Nome do Personagem",
        classe_pvp="Classe PvP",
        ap="Poder de ataque com gear pvp",
        aap="Poder de ataque awakening com gear pvp",
        dp="Poder de defesa"
    )
    async def atualizar(self, interaction: discord.Interaction,
                        ap: int,
                        aap: int,
                        dp: int, 
                        nome_familia: str = None,
                        nome_personagem: str = None,
                        classe_pvp: str = None
                        ):
        try:
            await interaction.response.defer(ephemeral=True)

            log_embed = discord.Embed(
            title="**Comando Executado**",
            description=f"**Comando:** */atualizar*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
            color=0xFFFFFF
            )
            log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

            log_channel = interaction.guild.get_channel(1318401148151009391)
            await log_channel.send(embed=log_embed)

            with sqlite3.connect('profiles.db') as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM profiles WHERE user_id = ?', (interaction.user.id,))
                existing_profile = c.fetchone()

            if not existing_profile:
                await interaction.followup.send(
                    "Perfil não encontrado. Use /registro para criar seu perfil.",
                    ephemeral=True
                )
                return
            
            nome_familia = self.preserve_caps(nome_familia) if nome_familia else existing_profile[1]
            nome_personagem = self.preserve_caps(nome_personagem) if nome_personagem else existing_profile[2]

            classe_pvp = classe_pvp.title() if classe_pvp else existing_profile[3]
            
            if classe_pvp not in class_mapping:
                invalido_embed = discord.Embed(
                    title="Classe Principal Inválida",
                    description=f"**Classe principal inválida. Classes disponíveis:**\n{', '.join(sorted(set(class_mapping.values())))}",
                    color=0xFF0000
                )
                await interaction.followup.send(embed=invalido_embed, ephemeral=True)
                #await interaction.followup.send(f"Classe principal inválida. Classes disponíveis: {', '.join(sorted(set(class_mapping.values())))}", ephemeral=True)
                return
            
            # Convert to full names
            main_class = class_mapping[classe_pvp]

            with sqlite3.connect('profiles.db') as conn:
                c = conn.cursor()
                c.execute('''
                    UPDATE profiles 
                    SET family_name = ?,
                        character_name = ?,
                        ap = ?,
                        aap = ?,
                        dp = ?,
                        main_class = ?,
                        last_updated = ?
                        
                    WHERE user_id = ?
                ''', (
                    nome_familia,
                    nome_personagem,
                    ap,
                    aap,
                    dp,
                    main_class,
                    datetime.now(),
                    interaction.user.id
                ))
                conn.commit()

            embed = discord.Embed(
                title="✅ Perfil Atualizado",
                description="Seu perfil foi atualizado com sucesso!\nUtilize /perfil para visualizar seu perfil.",
                color=0x00FF00
            )
            await interaction.followup.send(embed=embed, ephemeral=True)

            embed_log = discord.Embed(
                title="**Perfil Atualizado**",
                description=f"**Usuário:** {interaction.user.mention}\n**Família:** {nome_familia}\n**Personagem:** {nome_personagem}\n**AP:** {ap}\n**AAP:** {aap}\n**DP:** {dp}",
                color=0xFFFFFF,
                timestamp=datetime.now()
            )
            embed_log.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)

            log_channel = self.bot.get_channel(1318400984531210281)  # Your log channel ID
            if log_channel:
                await log_channel.send(embed=embed_log)

            print(f"{datetime.now()}: Perfil de {interaction.user.display_name} atualizado com sucesso.")

        except Exception as e:
            print(f"Error in atualizar: {e}")
            await interaction.followup.send("Erro ao atualizar perfil.", ephemeral=True)

    @app_commands.command(name="perfil", description="Mostra seu perfil")
    @app_commands.checks.has_role(1361472124199637102)
    @app_commands.guild_only()
    async def perfil(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)

            log_embed = discord.Embed(
            title="**Comando Executado**",
            description=f"**Comando:** */perfil*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
            color=0xFFFFFF
            )
            log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

            log_channel = interaction.guild.get_channel(1318401148151009391)
            await log_channel.send(embed=log_embed)

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
            
            lollipop_avg = await self.get_lollipop_average()
            guild_avg = await self.get_guild_average(interaction.user)
            class_avg = await self.get_class_average(data[3])

            user_gs = int(((data[4] + data[5]) / 2) + data[6])
            
            role_guilda = await self.get_guildas(interaction.user)
            role_raid = await self.get_raids(interaction.user)

            aps = data[4] + data[5]  # AP + AAP
            ap2 = aps / 2  # AP + AAP * 2
            gs = int(ap2 + data[6])  # APS + DP

            embed = discord.Embed(
                title=f"{interaction.user.display_name}",
                color=0x3d85c6,
            #    timestamp=datetime.now()
            )            
            embed.add_field(name="📄Família", value=data[1], inline=True)
            embed.add_field(name="📄Personagem", value=data[2], inline=True)
            embed.add_field(name="🔰Guilda", value=role_guilda if role_guilda else "Sem guilda⚠️", inline=True)
            #embed.add_field(name="\u200b", value="\u200b", inline=True)
            embed.add_field(name="🚩Raid", value=role_raid if role_raid else "Sem raid⚠️", inline=True)
            embed.add_field(name="🆑asse PvP", value=data[3], inline=True)
            #embed.add_field(name="\u200b", value="\u200b", inline=True)
            embed.add_field(name="🗡️AP Pre/Succ", value=data[4], inline=True)
            embed.add_field(name="⚔️AP Awakening", value=data[5], inline=True)
            embed.add_field(name="🛡️DP", value=data[6], inline=True)
            embed.add_field(name="🏆Gearscore", value=f"{gs}", inline=True)

            embed.add_field(
                name="📊Média (Lollipop)",
                value="Acima ✅" if user_gs >= (lollipop_avg or 0) else "Abaixo ⚠️",
                inline=True
            )

            if guild_avg:
                guild_name = next(name for id, name in self.guildas.items()
                                if id in [r.id for r in interaction.user.roles])
                embed.add_field(
                    name=f"📊Média ({guild_name})",
                    value="Acima ✅" if user_gs >= guild_avg else "Abaixo ⚠️",
                    inline=True
                )
            else:
                embed.add_field(name="📊Média (Guilda)", value="Sem guilda⚠️", inline=True                
                )

            embed.add_field(
                name=f"📊Média ({data[3]})",
                value="Acima ✅" if class_avg and gs >= class_avg else "Abaixo ⚠️",
                inline=True
            )


            #embed.add_field(name="📎Link Gear", value=(data[9] if data[9] else "⚠️Nenhum link"), inline=True)
            embed.add_field(name="📎Link Gear", value=f"[Clique aqui]({data[8]})" if data[8] and data[8].strip() else "Nenhum link", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)
            embed.add_field(name="📅Criado em", value=(data[7])[:16], inline=True)
            
            embed.set_thumbnail(url=interaction.user.avatar.url if interaction.user.avatar else interaction.user.default_avatar.url)
            embed.set_footer(text=f"{data[3]} {gs}gs | Atualizado em {data[9][:16]}")
            
            await interaction.followup.send(embed=embed, ephemeral=True)

            if user_gs < (lollipop_avg or 0):
                lollipop_gs_baixo_embed = discord.Embed(
                    title="⚠️ Atenção!",
                    description=f"Seu Gearscore ({user_gs}) está abaixo da média da Lollipop.\n"
                )

                await interaction.followup.send(embed=lollipop_gs_baixo_embed, ephemeral=True)

            if guild_avg is not None and user_gs < guild_avg:
                guild_gs_baixo_embed = discord.Embed(
                    title="⚠️ Atenção!",
                    description=f"Seu Gearscore ({user_gs}) está abaixo da média da {guild_name}.\n"
                )

                await interaction.followup.send(embed=guild_gs_baixo_embed, ephemeral=True)

            if user_gs < class_avg:
                class_gs_baixo_embed = discord.Embed(
                    title="⚠️ Atenção!",
                    description=f"Seu Gearscore ({user_gs}) está abaixo da média da sua classe.\n"
                )

                await interaction.followup.send(embed=class_gs_baixo_embed, ephemeral=True)
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
                placeholder="Trocar Raid",
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
                    await interaction.response.send_message(f"Raid atualizada para {self.bot.get_cog('Recruit').raids[new_role_id]}", ephemeral=True)
                
            except Exception as e:
                print(f"Error in raid selection: {e}")
                await interaction.response.send_message("Erro ao atualizar raid.", ephemeral=True)

    class GuildSelectView(View):
        def __init__(self, bot, target_user):
            super().__init__()
            self.bot = bot
            self.target_user = target_user
        
            # Create guild selection menu
            select = Select(
                placeholder="Trocar Guilda",
                options=[
                    discord.SelectOption(label=guild_name, value=str(guild_id))
                    for guild_id, guild_name in bot.get_cog('Recruit').guildas.items()
                ]
            )
            select.callback = self.guild_callback
            self.add_item(select)

        async def guild_callback(self, interaction: discord.Interaction):
            try:
                # Get the selected guild role ID
                new_role_id = int(interaction.data['values'][0])
                guild = interaction.guild
                member = guild.get_member(self.target_user.id)

               # Remove existing guild roles
                for guild_id in self.bot.get_cog('Recruit').guildas.keys():
                    role = guild.get_role(guild_id)
                    if role and role in member.roles:
                        await member.remove_roles(role)
            
                # Add new guild role
                new_role = guild.get_role(new_role_id)
                if new_role:
                    await member.add_roles(new_role)
                    await interaction.response.send_message(
                        f"Guilda atualizada para {self.bot.get_cog('Recruit').guildas[new_role_id]}",
                        ephemeral=True
                    )
            
            except Exception as e:
                print(f"Error in guild selection: {e}")
                await interaction.response.send_message("Erro ao atualizar guilda.", ephemeral=True)

    @perfil.error
    async def perfil_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message("Você não tem permissão para usar este comando. Adicione o cargo <@&1361472124199637102> para utilizar este comando.", ephemeral=True)
        else:
            print(f'Error in pre command: {error}')

    @app_commands.command(name="pre", description="Mostra o perfil de outro usuário")
    @app_commands.describe(user="Usuário para verificar o perfil")
    @app_commands.guild_only()
    @app_commands.checks.has_role(1361472124199637102)
    async def pre(self, interaction: discord.Interaction, user: discord.User):
        try:
            await interaction.response.defer(ephemeral=True)

            log_embed = discord.Embed(
            title="**Comando Executado**",
            description=f"**Comando:** */pre*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
            color=0xFFFFFF
            )
            log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

            log_channel = interaction.guild.get_channel(1318401148151009391)
            await log_channel.send(embed=log_embed)

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

            aps = data[4] + data[5]  # AP + AAP
            ap2 = aps / 2  # AP + AAP * 2
            gs = int(ap2 + data[6])  # APS + DP

            embed = discord.Embed(
                title=f"Perfil de {user.display_name}",
                color=0x3d85c6,
            #    timestamp=datetime.now()
            )            
            embed.add_field(name="📄Família", value=data[1], inline=True)
            embed.add_field(name="📄Personagem", value=data[2], inline=True)
            embed.add_field(name="🔰Guilda", value=role_guilda if role_guilda else "Sem guilda⚠️", inline=True)
            #embed.add_field(name="\u200b", value="\u200b", inline=True)
            embed.add_field(name="🚩Raid", value=role_raid if role_raid else "Sem raid⚠️", inline=True)
            embed.add_field(name="🆑asse PvP", value=data[3], inline=True)
            #embed.add_field(name="\u200b", value="\u200b", inline=True)
            embed.add_field(name="🗡️AP Pre/Succ", value=data[4], inline=True)
            embed.add_field(name="⚔️AP Awakening", value=data[5], inline=True)
            embed.add_field(name="🛡️DP", value=data[6], inline=True)
            embed.add_field(name="🏆Gearscore", value=f"{gs}", inline=True)
            #embed.add_field(name="📎Link Gear", value=(data[9] if data[9] else "⚠️Nenhum link"), inline=True)
            embed.add_field(name="📎Link Gear", value=f"[Clique aqui]({data[8]})" if data[8] and data[8].strip() else "Nenhum link", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)
            embed.add_field(name="📅Criado em", value=(data[7])[:16], inline=True)
            
            embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
            embed.set_footer(text=f"{data[3]} {gs}gs | Atualizado em {data[9][:16]}")
            
            raid_view = Recruit.RaidSelectView(self.bot, user)
            guild_view = Recruit.GuildSelectView(self.bot, user)

            combined_view = View()
            
            for item in raid_view.children:
                combined_view.add_item(item)

            for item in guild_view.children:
                combined_view.add_item(item)

            await interaction.followup.send(embed=embed, view=combined_view, ephemeral=True)
            print(f"Requisitado por: {interaction.user.display_name} - Perfil de {user.display_name} mostrado com sucesso.")

        except Exception as e:
            print(f"Error in pre: {e}")
            await interaction.followup.send("Erro ao mostrar perfil.", ephemeral=True)

    @pre.error
    async def pre_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingRole):
            await interaction.response.send_message("Você não tem permissão para usar este comando. Adicione o cargo <@&1361472124199637102> para utilizar este comando.", ephemeral=True)
        else:
            print(f'Error in pre command: {error}')

    @app_commands.command(name="recrutar", description="Recruta um usuário para a guilda")
    @app_commands.describe(user="Usuário para recrutar", guilda="Guilda para recrutar o usuário")
    @app_commands.guild_only()
    @app_commands.checks.has_role(1326000068448489502) # Officer
    @app_commands.choices(guilda=[
        app_commands.Choice(name="Allyance", value="allyance"),
        app_commands.Choice(name="Grand Order", value="grand_order"),
        app_commands.Choice(name="Manifest", value="manifest")
    ])
    async def recrutar(self, interaction: discord.Interaction, user: discord.User, guilda: app_commands.Choice[str]):
        try:
            await interaction.response.defer(ephemeral=True)

            log_embed = discord.Embed(
            title="**Comando Executado**",
            description=f"**Comando:** */recrutar*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
            color=0xFFFFFF
            )
            log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

            log_channel = interaction.guild.get_channel(1318401148151009391)
            await log_channel.send(embed=log_embed)


            await user.send(
                f"Olá {user.mention}, você foi recrutado para a guilda {interaction.guild.name}!\n"
                "Por favor, use o comando /registro para iniciar" \
                "seu registro."
            )
            await user.send(file=discord.File("C:/Users/rf/Pictures/exemplo_perfil.png"))  # Optional image
            await interaction.followup.send(f"Recrutamento enviado para {user.display_name}.", ephemeral=True)

            if guilda.value == "allyance":
                role_id = 929344073221935104
                agregistro = 1392610552794189866
                await user.add_roles(interaction.guild.get_role(role_id, reason="Recrutamento Allyance"))
                await user.add_roles(interaction.guild.get_role(agregistro, reason="Recrutamento Allyance"))
                print(f"{datetime.now()}: Cargo {interaction.guild.get_role(role_id).name} adicionado a {user.display_name}")
            elif guilda.value == "grand_order":
                role_id = 935733958266716200
                agregistro = 1392610552794189866
                await user.add_roles(interaction.guild.get_role(role_id, reason="Recrutamento Grand Order"))
                await user.add_roles(interaction.guild.get_role(agregistro, reason="Recrutamento Grand Order"))
                print(f"{datetime.now()}: Cargo {interaction.guild.get_role(role_id).name} adicionado a {user.display_name}")
            elif guilda.value == "manifest":
                role_id = 1206381250064158740
                agregistro = 1392610552794189866
                await user.add_roles(interaction.guild.get_role(role_id, reason="Recrutamento Manifest"))
                await user.add_roles(interaction.guild.get_role(agregistro, reason="Recrutamento Manifest"))
                print(f"{datetime.now()}: Cargo {interaction.guild.get_role(role_id).name} adicionado a {user.display_name}")
            else:
                await interaction.followup.send("Guilda inválida selecionada.", ephemeral=True)
                return

        except Exception as e:
            print(f"Error in recrutar: {e}")
            await interaction.followup.send("Erro ao enviar recrutamento.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Recruit(bot))