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

        self.cogslist = ["cogs.help_cog", "cogs.music_cog", "cogs.gpt_cog", "cogs.welcome_cog", "cogs.ticket_cog", "cogs.todolist_cog", "cogs.schedule_cog"]

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
async def reload(interaction: discord.Interaction, cog:Literal["help_cog", "music_cog", "gpt_cog", "welcome_cog", "ticket_cog", "todolist_cog"]):
    try:
        await client.reload_extension(name="cogs."+cog.lower())
        await interaction.response.send_message(f"Successfully reloaded **{cog}.py**", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"Failed to reload **{cog}.py**. See error below\n ```{e}```", ephemeral=True)


@client.tree.command(name="userinfo", description="Shows your user info.")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):
    if member is None:
        member = interaction.user

    roles = [role for role in member.roles]
    embed = discord.Embed(
        title="User info",
        description=f"Here's the user info on the user {member.name}",
        color=discord.Color.green(),
        timestamp=interaction.created_at,
    )
    embed.set_thumbnail(url=member.avatar)
    embed.add_field(name="ID", value=member.id)
    embed.add_field(name="Name", value=f"{member.name}")
    embed.add_field(name="Nickname", value=member.display_name)

    # Convert Status enum to a string
    embed.add_field(name="Created At", value=member.created_at.strftime("%a, %B %#d, %Y, %I:%M %p"))
    embed.add_field(name="Joined At", value=member.joined_at.strftime("%a, %B %#d, %Y, %I:%M %p"))

    # Check if @everyone is in roles and handle it differently
    if discord.utils.get(member.roles, name="@everyone"):
        embed.add_field(name="Roles", value="Everyone")
    else:
        embed.add_field(name=f"Roles ({len(roles)})", value=" ".join(role.mention for role in roles))

    embed.add_field(name="Top Role", value=member.top_role.mention)
    embed.add_field(name="Bot?", value=member.bot)

    await interaction.response.send_message(embed=embed)


keep_alive()
client.run(config.TOKEN)