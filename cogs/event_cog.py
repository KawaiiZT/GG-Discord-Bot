from discord import app_commands
from discord.ext import commands
from discord.ui import View
from discord import ButtonStyle
from discord.ui import Button, View



class EventCountdown(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.event_date = None
        self.task = None

class SetEventDateView(View):
    def __init__(self):
        super().__init__()
        self.add_item(Button(label="Set Event Date", custom_id="set_event_date", style=ButtonStyle.primary))

    async def interaction_check(self, interaction: discord.Interaction):
        return interaction.user == self.message.author

    @commands.command(name="eventcreate", description="Create a new event")
    async def event_create(self, ctx):
        view = SetEventDateView()
        await ctx.send("Click the button to set the event date.", view=view)

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        if interaction.custom_id == "set_event_date":
            await interaction.response.send_message("Please enter the event date in YYYY-MM-DD format.")
            try:
                date_interaction = await self.client.wait_for(
                    "message",
                    check=lambda m: m.author.id == interaction.user.id and m.channel.id == interaction.channel.id,
                    timeout=60,
                )
                self.event_date = datetime.datetime.strptime(date_interaction.content, '%Y-%m-%d')
                self.task = self.client.loop.create_task(self.countdown(interaction))
                await interaction.response.send_message(f'Event date set to {self.event_date.strftime("%Y-%m-%d")}.')
            except (asyncio.TimeoutError, ValueError):
                await interaction.response.send_message("Timeout or incorrect date format. Please try again.")