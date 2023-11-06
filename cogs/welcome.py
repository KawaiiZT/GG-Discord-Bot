import discord
import datetime
from discord.ext import commands
from discord import app_commands

#idของChannelในDiscord
welcome_channel = 1152256157604392982

bot = commands.Bot(command_prefix='.', intents=discord.Intents.default())

class welcome(commands.Cog):
    @bot.event
    async def on_member_join(member):
        channel  = bot.get_channel(welcome_channel)
        embed = discord.Embed(
            description=f'ยินดีต้อนรับ **{member.mention}** เข้าสู่เซิพเวอร์.',
            color=0xff55ff,
            timestamp=datetime.datetime.now()
        )
        role = discord.utils.get(member.guild.roles, name='Member')
        await member.add_roles(role)
        await channel.send(embed=embed)

async def setup(client:commands.Bot) -> None:
    await client.add_cog(welcome(client))