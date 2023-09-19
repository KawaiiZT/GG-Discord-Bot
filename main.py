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

#bot says hello to the user / for test purposes
@client.tree.command(name="hello", description="Bot says hi to you")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}! This is GG study bot!",\
        ephemeral=True)

#say command(kinda like tts) / for test purposes
@client.tree.command(name="say", description="What should I say?")
async def say(interaction: discord.Interaction, thingtosay: str):
    await interaction.response.send_message(f"{interaction.user.name} said: `{thingtosay}`")


client.run(config.TOKEN)

