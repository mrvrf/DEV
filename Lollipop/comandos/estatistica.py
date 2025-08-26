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

classes = {
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

def fetch_profiles():
    conn = sqlite3.connect("profiles.db")
    cursor = conn.cursor()
    cursor.execute("""
        SELECT user_id, family_name, ap, aap, dp, main_class
        FROM profiles
    """)
    rows = cursor.fetchall()
    conn.close()
    # Map Discord ID (string) to profile data
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

        await interaction.response.defer()  # in case it takes a moment

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
                gs = ((ap + aap) / 2) + dp
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

            members_embed = discord.Embed(
                title="Membros (Geral)",
                color=discord.Color.gold(),
                timestamp=datetime.now()
            )

            members_list = []
            for i, member in enumerate(all_members, 1):
                members_list.append(f"**{i}.** {member['family_name']} ({member['main_class']}) - {int(member['gs'])}gs")

            for i in range(0, len(members_list), 50):
                chunk = members_list[i:i+50]
                members_embed.add_field(
                    name=f"Membros {i+1}-{i+len(chunk)}" if i > 0 else "Membros",
                    value="\n".join(chunk),
                    inline=False
                )
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

            await interaction.followup.send(embeds=[members_embed, classes_embed], ephemeral=True)
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
            gs = ((ap + aap) / 2) + dp
            stats_list.append({"family_name": family_name, "gs": gs, "main_class": main_class})

        # Sort by GS
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
            embed.set_thumbnail(url=interaction.guild.icon.url if interaction.guild.icon else None)


        await interaction.followup.send(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Stats(bot))