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
            embed = discord.Embed(title=f'Welcome {member} to {guild.name}',
                description=f'ยินดีต้อนรับ **{member.mention}** เข้าสู่เซิพเวอร์ {guild.name}.',
                color=0xff55ff,
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="หากต้องการความช่วยเหลือ ❗", value="สามารถใช้ /help ได้เลย")
            embed.set_image(url='https://media.tenor.com/vAdNbp-gxFUAAAAd/welcome-discord.gif') #รูปตอน Welcome
            embed.set_author(name=member.display_name, icon_url=member.avatar.url)
            embed.set_thumbnail(url=member.avatar.url)
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