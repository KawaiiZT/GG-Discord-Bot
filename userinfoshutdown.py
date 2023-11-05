import discord
from discord.ext import commands
from colorama import Back, Fore, Style
import time
import platform

client = commands.Bot(command_prefix=".", intents=discord.Intents.all())

@client.command()
async def hello(ctx):
    await ctx.send("hello!")

@client.event
async def on_ready():
    prfx = (Back.BLACK + Fore.GREEN + time.strftime("%H:%M:%S UTC", time.gmtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)
    print(prfx + " Logged in as " + Fore.YELLOW + client.user.name)
    print(prfx + " Bot ID " + Fore.YELLOW + str(client.user.id))
    print(prfx + " Discord Version " + Fore.YELLOW + discord.__version__)
    print(prfx + " Python Version " + Fore.YELLOW + str(platform.python_version()))

@client.command(aliases=['close','stop'])
async def shutdown(ctx):
    await ctx.send("Shutting down the bot")
    await client.close()

@client.command(aliases=['uinfo','whois'])
async def userinfo(ctx, member:discord.Member=None):
    if member == None:
        member = ctx.message.author
    roles = [role for role in member.roles]
    embed = discord.Embed(title="User info", description=f"Here's the user info on the user {member.name}", color=discord.Color.green(), timestamp = ctx.message.created_at)
    embed.set_thumbnail(url=member.avatar)
    embed.add_field(name="ID", value = member.id)
    embed.add_field(name="Name", value = f"{member.name}#{member.discriminator}")
    embed.add_field(name="Nickmame", value = member.display_name)
    embed.add_field(name="Status", value = member.status)
    embed.add_field(name="Created At", value = member.created_at.strftime("%a, %B %#d, %Y, %I:%M %p"))
    embed.add_field(name="Joined At", value = member.created_at.strftime("%a, %B %#d, %Y, %I:%M %p"))
    embed.add_field(name=f"Roles ({len(roles)})", value = " ".join({role.mention for role in roles}))
    embed.add_field(name="Top Role", value = member.top_role.mention)
    embed.add_field(name="Messages", value ="0")
    embed.add_field(name="Bot?", value = member.bot)
    await ctx.send(embed=embed)
