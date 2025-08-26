import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
import statistics
from datetime import datetime
from collections import Counter

# Mapping of guild option values → role IDs
GUILD_ROLE_IDS = {
    "lollipop": 1361472124199637102,
    "allyance": 929344073221935104,
    "grand_order": 935733958266716200,
    "manifest": 1206381250064158740
}

raids_ids = {
    "elefanteiro": 942684778510045205,
    "flanco": 978853483782492180,
    "bandeira": 1244387844961603766,
    "raid_1": 1210354501870166077,
    "raid_2": 1210354582048473088,
    "raid_3": 1210354616840093796,
    "raid_4": 1210354659378860083,
    "defesa": 959267503475949578
}

classes = {
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

def fetch_profiles():
    conn = sqlite3.connect("profiles.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, family_name, ap, aap, dp, main_class
        FROM profiles
    """)
    rows = cursor.fetchall()
    conn.close()
    return {str(user_id): (family_name, ap, aap, dp, main_class) for user_id, family_name, ap, aap, dp, main_class in rows}

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="stats", description="Mostra estatísticas das guildas")
    @app_commands.describe(guild_name="Escolha a guilda para ver as estatísticas")
    @app_commands.guild_only()
    @app_commands.checks.has_role(1325386396214628454)
    @app_commands.choices(guild_name=[
        app_commands.Choice(name="Geral", value="geral"),
        app_commands.Choice(name="Lollipop", value="lollipop"),
        app_commands.Choice(name="Allyance", value="allyance"),
        app_commands.Choice(name="Grand Order", value="grand_order"),
        app_commands.Choice(name="Manifest", value="manifest")
    ])
    async def stats(self, interaction: discord.Interaction, guild_name: app_commands.Choice[str]):
        log_embed = discord.Embed(
            title="**Comando Executado**",
            description=f"**Comando:** */stats*\n**Hora:** {datetime.now().strftime('%d/%m/%Y | %H:%M')}",
            color=0xFFFFFF
        )
        log_embed.set_footer(text=f"Executado por {interaction.user.display_name}", icon_url=interaction.user.avatar.url)

        log_channel = interaction.guild.get_channel(1318401148151009391)
        await log_channel.send(embed=log_embed)

        await interaction.response.defer()

        if guild_name.value == "geral":

            role = interaction.guild.get_role(1395196503261446146)
            if not role:
                return await interaction.followup.send("Cargo não encontrado.", ephemeral=True)
            
            profiles = fetch_profiles()
            members_in_role = [m for m in role.members if str(m.id) in profiles]

            if not members_in_role:
                return await interaction.followup.send("Nenhum jogador encontrado para essa guilda.", ephemeral=True)
            
            all_members = []
            class_stats = {}

            for member in members_in_role:
                family_name, ap, aap, dp, main_class = profiles[str(member.id)]
                max_ap = max(ap, aap)
                gs = max_ap + dp
                #gs = ((ap + aap) / 2) + dp
                all_members.append({"family_name": family_name, "gs": gs, "main_class": main_class})

                if main_class not in class_stats:
                    class_stats[main_class] = {"count": 0, "total_gs": 0}
                class_stats[main_class]["count"] += 1
                class_stats[main_class]["total_gs"] += gs

            all_members.sort(key=lambda x: x["gs"], reverse=True)

            class_averages = []
            for class_name, stats in class_stats.items():
                avg_gs = stats["total_gs"] / stats["count"]
                class_averages.append({"class_name": class_name, "avg_gs": avg_gs})
            class_averages.sort(key=lambda x: x["avg_gs"], reverse=True)

            member_embeds = []
            chunk_size = 30
            for chunk_index in range(0, len(all_members), chunk_size):
                chunk = all_members[chunk_index:chunk_index + chunk_size]
                
                embed = discord.Embed(
                    title=f"Membros (Geral) - Parte {chunk_index//chunk_size + 1}",
                    color=discord.Color.gold(),
                    timestamp=datetime.now()
                )
                
                members_list = []
                for i, member in enumerate(chunk, chunk_index + 1):
                    members_list.append(f"**{i}.** {member['family_name']} ({member['main_class']}) - {int(member['gs'])}gs")
                
                embed.description = "\n".join(members_list)
                member_embeds.append(embed)

            classes_embed = discord.Embed(
                title="Estatísticas por Classe",
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )

            classes_list = []
            for i, class_stat in enumerate(class_averages, 1):
                class_name = class_stat["class_name"]
                count = class_stats[class_name]["count"]
                avg_gs = int(class_stat["avg_gs"])
                classes_list.append(f"**{i}.** {class_name} - {count} jogadores - {avg_gs}gs")
            
            classes_embed.description = "\n".join(classes_list)

            all_embeds = member_embeds + [classes_embed]
            await interaction.followup.send(embeds=all_embeds[:10], ephemeral=True)  

            if len(all_embeds) > 10:
                for i in range(10, len(all_embeds), 10):
                    chunk = all_embeds[i:i+10]
                    await interaction.followup.send(embeds=chunk, ephemeral=True)
            return

        role_id = GUILD_ROLE_IDS[guild_name.value]
        role = interaction.guild.get_role(role_id)
        if not role:
            return await interaction.followup.send(f"Cargo para `{guild_name.name}` não encontrado.", ephemeral=True)

        profiles = fetch_profiles()
        members_in_role = [m for m in role.members if str(m.id) in profiles]
        if not members_in_role:
            return await interaction.followup.send("Nenhum jogador encontrado para essa guilda.", ephemeral=True)

        stats_list = []
        for member in members_in_role:
            family_name, ap, aap, dp, main_class = profiles[str(member.id)]
            max_ap = max(ap, aap)
            gs = max_ap + dp
        #    gs = ((ap + aap) / 2) + dp
            stats_list.append({"family_name": family_name, "gs": gs, "main_class": main_class})

        stats_list.sort(key=lambda x: x["gs"], reverse=True)

        median_gs = statistics.median([s["gs"] for s in stats_list])
        highest = stats_list[0]

        class_list = [
            classes.get(entry['main_class'], entry['main_class'])
            for entry in stats_list
        ]

        if guild_name.value == "todos":
            embed = discord.Embed(
                title="Membros ()",
                color=discord.Color.gold()
            )

        class_counts = Counter(class_list)
        top5_classes = class_counts.most_common(5)

        embed = discord.Embed(
            title=f"{guild_name.name}",
            color=discord.Color.gold()
        )
        embed.add_field(name="📊 GS Médio", value=f"{int(median_gs)}", inline=True)
        embed.add_field(name="🏆 Membro Top GS", value=f"👑{highest['family_name']} ({int(highest['gs'])})", inline=True)
        embed.add_field(name="👥 Membros", value=str(len(stats_list)), inline=True)
        top10_lines = [
            f"**{i+1}.** {entry['family_name']} ({int(entry['gs'])})"
            for i, entry in enumerate(stats_list[:5])
        ]
        embed.add_field(name="💯 Top 5 Gearscore", value="\n".join(top10_lines), inline=True)
        top5_lines = [
            f"{cls} ({count})"
            for cls, count in top5_classes
        ]
        embed.add_field(name="⚔️ Top 5 Classes", value="\n".join(top5_lines), inline=True)
        if guild_name.value == "lollipop":
            # Calculate raid averages
            raid_stats = {}
            for raid_name, raid_id in raids_ids.items():
                raid_role = interaction.guild.get_role(raid_id)
                if raid_role:
                    raid_members = [m for m in raid_role.members if str(m.id) in profiles]
                    if raid_members:
                        raid_gs = []
                        for member in raid_members:
                            family_name, ap, aap, dp, main_class = profiles[str(member.id)]
                            max_ap = max(ap, aap)
                            gs = max_ap + dp
                        #    gs = ((ap + aap) / 2) + dp
                            raid_gs.append(gs)
                        raid_stats[raid_name] = int(sum(raid_gs) / len(raid_gs))
                    else:
                        raid_stats[raid_name] = 0
            
            excluded_role_ids = [1079803777462308997, 959267503475949578, 1237892599357116436]

            filtered_stats = []
            for member in members_in_role:
                has_excluded_role = any(discord.utils.get(member.roles, id=role_id)
                                        for role_id in excluded_role_ids)
                
                if not has_excluded_role:
                    family_name, ap, aap, dp, main_class = profiles[str(member.id)]
                    max_ap = max(ap, aap)
                    gs = max_ap + dp
                    filtered_stats.append(gs)

            if filtered_stats:
                special_avg = int(sum(filtered_stats) / len(filtered_stats))
                embed.add_field(
                    name="⚔️ GS Médio (Filtro)",
                    value=f"{special_avg} gs - {len(filtered_stats)} membros",
                    inline=False
                )
            else:
                embed.add_field(
                    name="⚔️ GS Médio (Filtro)",
                    value="Sem membros",
                    inline=False
                )

            embed.add_field(name="\u200b", value="\u200b", inline=False)  # Spacer
            embed.add_field(name="📊 Média por Raid", value="", inline=False)
            
            for raid_name, avg_gs in raid_stats.items():
                formatted_name = raid_name.replace('_', ' ').title()
                embed.add_field(
                    name=f"⚔️ {formatted_name}",
                    value=f"{avg_gs}gs" if avg_gs > 0 else "Sem membros",
                    inline=True
                )

            no_raid_gs = []
            for member in members_in_role:
                has_raid = False
                for raid_id in raids_ids.values():
                    if discord.utils.get(member.roles, id=raid_id):
                        has_raid = True
                        break
                if not has_raid:
                    family_name, ap, aap, dp, main_class = profiles[str(member.id)]
                    max_ap = max(ap, aap)
                    gs = max_ap + dp
                #    gs = ((ap + aap) / 2) + dp
                    no_raid_gs.append(gs)

            if no_raid_gs:
                avg_no_raid = int(sum(no_raid_gs) / len(no_raid_gs))
                embed.add_field(
                    name="⚔️ Sem Raid",
                    value=f"{avg_no_raid}gs",
                    inline=True
                )
            else:
                embed.add_field(
                    name="⚔️ Sem Raid",
                    value="Sem membros",
                    inline=True
                )
        if guild_name.value == "lollipop":
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Stats(bot))