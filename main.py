import discord
from discord.ext import commands
import config

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix='!', intents=intents)

@client.event
async def on_ready():
    print("-----------------------------")
    print("The bot is now ready for use!")
    print("-----------------------------")

@client.command()
async def hello(ctx):
    await ctx.send("Hello, I am GG Study bot")

@client.command()
async def test(ctx):
    await ctx.send("Test: Great!")

client.run(config.TOKEN)

