import discord
import datetime
from discord.ext import commands

class welcome(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        for guild in self.client.guilds:
            # Send the welcome message
            embed = discord.Embed(
                description=f'ยินดีต้อนรับ **{member.mention}** เข้าสู่เซิพเวอร์ {guild.name}.',
                color=0xff55ff,
                timestamp=datetime.datetime.now()
            )
            default_channel = guild.text_channels[0]
            await default_channel.send(embed=embed)

            # Add the "Member" role
            role = discord.utils.get(guild.roles, name='Member')
            if role:
                await member.add_roles(role)
            else:
                pass

async def setup(client: commands.Bot) -> None:
    await client.add_cog(welcome(client))
