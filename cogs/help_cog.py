import discord
from discord.ui import Select, View
from discord.ext import commands
from discord import app_commands

class help(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client

    @app_commands.command(name="help", description="Find about commands")
    async def help(self, interaction: discord.Interaction):
        select = Select(options= [
            discord.SelectOption(label="Music", emoji = "🎶"),
            discord.SelectOption(label="Attandance", emoji = "✅"),
            discord.SelectOption(label="ChatGPT", emoji= "❓"),
        ])
        
        async def my_callback(interaction):
            if select.values[0] == "Music":
                print("I'm here to help please wait for me.")
            await interaction.response.send_message(f"You chose: {select.values[0]}")
        select.callback = my_callback
        view = View()
        view.add_item(select)
        await interaction.response.send_message(f"Choose a category", view=view)

async def setup(client:commands.Bot) -> None:
    await client.add_cog(help(client))