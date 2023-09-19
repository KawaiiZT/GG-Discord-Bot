import discord
from discord import app_commands
from discord.ext import commands
import config

client = commands.Bot(command_prefix="!", intents = discord.Intents.all())

@client.event
async def on_ready():
    print("Bot is up and ready!")
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands(s)")
    except Exception as e:
        print(e)

@client.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}! This is GG study bot!",\
        ephemeral=True)

@client.tree.command(name="say")
@app_commands.describe(arg="What should i say?")
async def say(interaction: discord.Interaction, arg: str):
    await interaction.response.send_message(f"{interaction.user.name} said: `{arg}`")

client.run(config.TOKEN)

