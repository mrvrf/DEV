import discord
from discord.ext import commands
from discord import app_commands
import json
import os

# Load the state of the lists from a JSON file
lists = {'list1': [], 'list2': []}
if os.path.exists('lists.json'):
    try:
        with open('lists.json', 'r') as f:
            lists = json.load(f)
    except json.JSONDecodeError:
        pass  # If there's an error, keep the default empty lists

# Load the message ID from a file
message_id = None
if os.path.exists('message_id.json'):
    try:
        with open('message_id.json', 'r') as f:
            message_id = json.load(f).get('message_id')
    except json.JSONDecodeError:
        pass  # If there's an error, keep message_id as None

class MyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Botão 1", style=discord.ButtonStyle.primary, custom_id="button1")
    async def button1(self, interaction: discord.Interaction, button: discord.ui.Button):
        nickname = interaction.user.display_name
        if nickname in lists['list1']:
            lists['list1'].remove(nickname)
        else:
            lists['list1'].append(nickname)
        await self.update_embed(interaction)

    @discord.ui.button(label="Botão 2", style=discord.ButtonStyle.primary, custom_id="button2")
    async def button2(self, interaction: discord.Interaction, button: discord.ui.Button):
        nickname = interaction.user.display_name
        if nickname in lists['list2']:
            lists['list2'].remove(nickname)
        else:
            lists['list2'].append(nickname)
        await self.update_embed(interaction)

    async def update_embed(self, interaction):
        embed = discord.Embed(title="testes")
        embed.add_field(name="Lista 1", value="\n".join(lists['list1']) or "Empty", inline=False)
        embed.add_field(name="Lista 2", value="\n".join(lists['list2']) or "Empty", inline=False)
        await interaction.response.edit_message(embed=embed, view=self)
        with open('lists.json', 'w') as f:
            json.dump(lists, f)

@app_commands.command(name="embed", description="ene")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
async def create_embed(interaction: discord.Interaction):
    embed = discord.Embed(title="testes")
    embed.add_field(name="Lista 1", value="Empty", inline=False)
    embed.add_field(name="Lista 2", value="Empty", inline=False)
    message = await interaction.response.send_message(embed=embed, view=MyView())
    # Save the message ID to a file
    message = await interaction.original_response()
    with open('message_id.json', 'w') as f:
        json.dump({'message_id': message.id}, f)

async def setup(bot: commands.Bot):
    bot.tree.add_command(create_embed)
    if message_id:
        channel = bot.get_channel(1318400984531210281)  # Replace with your channel ID
        message = await channel.fetch_message(message_id)
        await message.edit(view=MyView())