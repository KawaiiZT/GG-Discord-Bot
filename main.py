import discord
import openai
import config
import os
import asyncio
import time
import json
import platform

from discord.utils import get
from discord import app_commands
from discord.ext import commands
from keep_alive import keep_alive
from colorama import Back, Fore, Style
from typing import Literal


class Client(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('.'), intents=discord.Intents().all(), help_command=None)

        self.cogslist = ["cogs.help_cog", "cogs.music_cog", "cogs.gpt_cog", "cogs.welcome_cog", "cogs.ticket_cog"]

    async def setup_hook(self):
        for ext in self.cogslist:
            await self.load_extension(ext)

    async def on_ready(self):
        prfx = (Back.BLACK + Fore.GREEN + time.strftime("%H:%M:%S GMT", time.localtime()) + \
            Back.RESET + Fore.WHITE + Style.BRIGHT)
        print(prfx + " Logged in as " + Fore.YELLOW + self.user.name)
        print(prfx + " Bot ID " + Fore.YELLOW + str(self.user.id))
        print(prfx + " Discord.py Version " + Fore.YELLOW + discord.__version__)
        synced = await self.tree.sync()
        print(prfx + " Synced " + Fore.YELLOW + str(len(synced)) + " Commands")


client = Client()
@client.tree.command(name="reload", description="reload cog file")
async def reload(interaction: discord.Interaction, cog:Literal["help_cog", "music_cog", "gpt_cog", "welcome_cog", "ticket_cog"]):
    try:
        await client.reload_extension(name="cogs."+cog.lower())
        await interaction.response.send_message(f"Successfully reloaded **{cog}.py**", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to reload **{cog}.py**. See error below\n ```{e}```", ephemeral=True)




keep_alive()
client.run(config.TOKEN)