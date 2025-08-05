import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Modal, TextInput, View, Button
from datetime import datetime
import re
import aiosqlite
import os
import json
import asyncio

class LinkModal(Modal):
    def __init__(self, channel_id: int, guild_id: int, cog):
        super().__init__(title="Cobrança - Tendão", timeout=1200)
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.cog = cog  # Store reference to cog

        self.link = TextInput(
            label="Link",
            placeholder="Coloque o link da print do tendão aqui",
            required=True,
            style=discord.TextStyle.short
        )
        self.description = TextInput(
            label="Descrição",
            placeholder="Adicione uma mensagem ou algo que queira comentar.",
            required=True,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.link)
        self.add_item(self.description)

    async def on_submit(self, interaction: discord.Interaction):
        if interaction.user.id in self.cog.submitted_users:
            await interaction.response.send_message("Você já enviou uma imagem para esta cobrança!", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)
            
            # Update database with user's response
            await self.cog.update_user_response(interaction.user.id, self.link.value)
            
            guild = interaction.client.get_guild(self.guild_id)
            if not guild:
                await interaction.followup.send("Servidor não encontrado.", ephemeral=True)
                return

            channel = guild.get_channel(self.channel_id)
            if not channel:
                await interaction.followup.send("Canal não encontrado.", ephemeral=True)
                return

            embed = discord.Embed(
                title=f"Resposta - {interaction.user.display_name}",
                description=f"{self.description.value}",
                color=0x45818e,
                timestamp=datetime.now()
            )
            embed.add_field(name="Link", value=f"{self.link.value}", inline=True)
            embed.set_image(url=self.link.value)  # Assuming the link is an image URL
            embed.set_footer(
                text=f"Respondido por {interaction.user.display_name}",
                icon_url=interaction.user.avatar.url if interaction.user.avatar else None
            )
            
            await channel.send(embed=embed)
            self.cog.submitted_users.add(interaction.user.id)  # Track submission
            await interaction.followup.send("Link enviado com sucesso!", ephemeral=True)
            
        except Exception as e:
            print(f"Error in modal submission: {e}")
            await interaction.followup.send(f"Erro ao enviar: {str(e)}", ephemeral=True)

class SubmitView(View):
    def __init__(self, channel_id: int, guild_id: int, cog):
        super().__init__(timeout=1200)
        self.channel_id = channel_id
        self.guild_id = guild_id
        self.cog = cog

    @discord.ui.button(label="Enviar Print", style=discord.ButtonStyle.primary)
    async def submit(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id in self.cog.submitted_users:
            await interaction.response.send_message("Você já enviou uma resposta para esta cobrança!", ephemeral=True)
            return

        modal = LinkModal(self.channel_id, self.guild_id, self.cog)
        await interaction.response.send_modal(modal)

class VODReviewCommand(commands.Cog):
    def __init__(self, bot: commands.Bot, channel_id: int):
        self.bot = bot
        self.channel_id = channel_id
        self.submitted_users = set()
        self.cobrancas_dir = "cobrancas"
        os.makedirs(self.cobrancas_dir, exist_ok=True)
        self.current_cobranca = None

    async def create_cobranca_file(self, interaction: discord.Interaction, role: discord.Role):
        date_str = datetime.now().strftime('%d_%m_%Y_%H_%M')
        filename = f"cobranca_{date_str}.json"
        
        cobranca_data = {
            "creator": interaction.user.display_name,
            "date": datetime.now().strftime('%d/%m/%Y %H:%M'),
            "role": role.name,
            "users": {}
        }
        
        for member in role.members:
            if not member.bot:
                cobranca_data["users"][str(member.id)] = {
                    "name": member.name,
                    "answered": "NO",
                    "link": None
                }
        
        filepath = os.path.join(self.cobrancas_dir, filename)
        with open(filepath, 'w') as f:
            json.dump(cobranca_data, f, indent=4)
            
        return filename

    async def update_user_response(self, user_id: int, link: str):
        if self.current_cobranca:
            filepath = os.path.join(self.cobrancas_dir, self.current_cobranca)
            with open(filepath, 'r+') as f:
                data = json.load(f)
                data["users"][str(user_id)]["answered"] = "YES"
                data["users"][str(user_id)]["link"] = link
                f.seek(0)
                json.dump(data, f, indent=4)
                f.truncate()

    @app_commands.command(name="teste_cobrar", description="Envia uma cobrança de tendão.")
    @app_commands.guild_only()
    @app_commands.describe(role="Cargo para enviar a cobrança", itens="Itens a serem cobrados")
    @app_commands.checks.has_role(1325386396214628454)
    async def vodreview(self, interaction: discord.Interaction, role: discord.Role, itens: str):
        try:
            # Defer immediately to prevent timeout
            await interaction.response.defer(ephemeral=True)
            print(f"Starting cobrança for role {role.name}")

            # Create cobrança file first
            self.current_cobranca = await self.create_cobranca_file(interaction, role)
            print(f"Created cobrança file: {self.current_cobranca}")

            # Send initial response
            await interaction.followup.send(f"Iniciando envio de cobranças...", ephemeral=True)

            # Clear previous submissions
            self.submitted_users.clear()

            # Send log embed
            log_embed = discord.Embed(
                title="**Comando Executado**",
                description=f"**Comando:** */teste_cobrar*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
                color=0xFFFFFF
            )
            log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", 
                               icon_url=interaction.user.avatar.url if interaction.user.avatar else None)

            # Send to log channel
            log_channel = interaction.guild.get_channel(1318401148151009391)
            if log_channel:
                await log_channel.send(embed=log_embed)

            # Send to announcement channel
            channel_id = interaction.guild.get_channel(1389344723763986514)
            if channel_id:
                iniciar_cobranca = discord.Embed(
                    title="**Cobrança Iniciada**",
                    description=f"Cobrança de {itens} iniciada por {interaction.user.mention} no cargo {role.mention}.",
                    color=0xffffff,
                    timestamp=datetime.now()
                )
                await channel_id.send(f"{interaction.user.mention}")
                await channel_id.send(embed=iniciar_cobranca)

            # Send DMs in chunks
            successful_dms = []
            failed_dms = []
            chunk_size = 2
            members_list = [m for m in role.members if not m.bot]

            for i in range(0, len(members_list), chunk_size):
                chunk = members_list[i:i + chunk_size]
                for member in chunk:
                    try:
                        view = SubmitView(self.channel_id, interaction.guild.id, self)
                        cobrar_embed = discord.Embed(
                            title=f"**Cobrança de {itens}**",
                            description=f"Olá {member.mention}, por favor envie a print do seu {itens}.\n\n*A resposta deve ser enviada em até 20 minutos!*",
                            color=0xcc0000,
                            timestamp=datetime.now()
                        )
                        await member.send(embed=cobrar_embed)
                        await member.send(":saluting_face:", view=view)
                        successful_dms.append(member.display_name)
                        print(f"Sent DM to {member.display_name}")
                        await asyncio.sleep(2)  # Prevent rate limiting
                    except discord.Forbidden:
                        failed_dms.append(member.display_name)
                        print(f"Failed to send DM to {member.display_name}")
                    except Exception as e:
                        print(f"Error sending DM to {member.display_name}: {e}")
                        failed_dms.append(member.display_name)

                # Send progress update
                await interaction.followup.send(
                    f"Progresso: {len(successful_dms)}/{len(members_list)} mensagens enviadas...", 
                    ephemeral=True
                )
                await asyncio.sleep(1)  # Prevent rate limiting

            # Send final summary
            summary = f"Cobrança enviada para {len(successful_dms)} membros do cargo {role.mention}\n"
            if failed_dms:
                summary += f"Falha ao enviar para: {', '.join(failed_dms)}"

            await interaction.followup.send(summary, ephemeral=True)
            print("Cobrança completed successfully")

        except Exception as e:
            print(f"Error in vodreview command: {e}")
            await interaction.followup.send(f"Erro ao executar comando: {str(e)}", ephemeral=True)

    @app_commands.command(name="cobrancas", description="Mostra todas as cobranças existentes")
    @app_commands.guild_only()
    @app_commands.checks.has_role(1325386396214628454)
    async def show_cobrancas(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            print("Processing /cobrancas command...")  # Debug log
            
            if not os.path.exists(self.cobrancas_dir):
                print(f"Directory not found: {self.cobrancas_dir}")  # Debug log
                await interaction.followup.send("Não há cobranças registradas.", ephemeral=True)
                return
            
            files = os.listdir(self.cobrancas_dir)
            if not files:
                print("No files found in directory")  # Debug log
                await interaction.followup.send("Não há cobranças registradas.", ephemeral=True)
                return
            
            # Sort files by creation date
            files.sort(key=lambda x: os.path.getctime(os.path.join(self.cobrancas_dir, x)), reverse=True)
            
            embed = discord.Embed(
                title="Status das Cobranças",
                color=0xffffff,
                timestamp=datetime.now()
            )
            
            for file in files[:10]:  # Limit to 10 most recent
                try:
                    filepath = os.path.join(self.cobrancas_dir, file)
                    print(f"Processing file: {filepath}")  # Debug log
                    
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        total_users = len(data["users"])
                        answered = sum(1 for user in data["users"].values() if user["answered"] == "YES")
                        
                        embed.add_field(
                            name=f"__Cobrança {data['date']}__",
                            value=f"**Criado por:** {data['creator']}\n"
                                  f"**Respondido:** {answered}/{total_users}",
                            inline=False
                        )
                except Exception as e:
                    print(f"Error processing file {file}: {e}")  # Debug log
                    continue
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            print("Command completed successfully")  # Debug log
            
        except Exception as e:
            print(f"Error in show_cobrancas: {e}")  # Debug log
            try:
                await interaction.followup.send("Erro ao mostrar cobranças.", ephemeral=True)
            except:
                print("Failed to send error message")  # Debug log

    @app_commands.command(name="cobranca", description="Mostra detalhes de uma cobrança específica")
    @app_commands.guild_only()
    @app_commands.describe(cobranca_name="Nome da cobrança (ex: cobranca_25_12_2023)")
    @app_commands.checks.has_role(1325386396214628454)
    async def show_cobranca_details(self, interaction: discord.Interaction, cobranca_name: str):
        try:
            await interaction.response.defer(ephemeral=True)
            
            filepath = os.path.join(self.cobrancas_dir, f"{cobranca_name}.json")
            if not os.path.exists(filepath):
                await interaction.followup.send("Cobrança não encontrada.", ephemeral=True)
                return
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            embed = discord.Embed(
                title=f"Detalhes da Cobrança - {data['date']}",
                description=f"Criado por: {data['creator']}\nCargo: {data['role']}",
                color=0xffffff,
                timestamp=datetime.now()
            )
            
            answered = []
            not_answered = []
            
            for user_id, user_data in data["users"].items():
                if user_data["answered"] == "YES":
                    answered.append(f"✅ {user_data['name']}: {user_data['link']}")
                else:
                    not_answered.append(f"❌ {user_data['name']}")
            
            if answered:
                embed.add_field(
                    name="Responderam:",
                    value="\n".join(answered) if len("\n".join(answered)) < 1024 else f"{len(answered)} usuários responderam",
                    inline=False
                )
            
            if not_answered:
                embed.add_field(
                    name="Não Responderam:",
                    value="\n".join(not_answered) if len("\n".join(not_answered)) < 1024 else f"{len(not_answered)} usuários não responderam",
                    inline=False
                )
            
            embed.set_footer(text=f"Total: {len(answered)}/{len(data['users'])} respostas")
            
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            print(f"Error in show_cobranca_details: {e}")
            await interaction.followup.send("Erro ao mostrar detalhes da cobrança.", ephemeral=True)

async def setup(bot: commands.Bot):
    channel_id = 1389344723763986514
    await bot.add_cog(VODReviewCommand(bot, channel_id))