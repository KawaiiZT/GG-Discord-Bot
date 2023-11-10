import discord
from discord import app_commands
from discord.ext import commands
from discord.utils import get

class Report(commands.Cog):
    def __init__(self, client):
        self.client = client
        
    class ReportModal(discord.ui.Modal):
        def __init__(self):
            super().__init__(title="Report User")
            self.user_name = discord.ui.TextInput(label= "User's Discord Name", placeholder="og. username", required=True, max_length=100,\
                style= discord.TextStyle.short)
            self.user_id = discord.ui.TextInput(label= "User's Discord ID", placeholder="To grab a user's ID, make sure Developer mode is on.",\
                required=True, max_length=100, style= discord.TextStyle.short)
            self.user_problem = discord.ui.TextInput(label= "What did they do.", placeholder="og. Broke rule #69", required=True, max_length=2000,\
                style= discord.TextStyle.paragraph)
            self.add_item(self.user_name)
            self.add_item(self.user_id)
            self.add_item(self.user_problem)
            
        
        async def on_submit(self, interaction: discord.Interaction):
            channel = interaction.guild.get_channel(1172467604267479131)

            # Debugging print statement
            print(f"Attempting to send report to channel: {channel}")

            # Extract values from the modal items
            user_name_value = self.user_name.value
            user_id_value = self.user_id.value
            user_problem_value = self.user_problem.value

            # Create an embed with the extracted values
            embed = discord.Embed(title="New Feedback report", color=discord.Color.red())
            embed.add_field(name="User's Discord Name", value=user_name_value)
            embed.add_field(name="User's Discord ID", value=user_id_value)
            embed.add_field(name="What did they do", value=user_problem_value)

            # Set the author to the user who submitted the form
            embed.set_author(name=interaction.user.name)

            try:
                # Debugging print statement
                print(f"Attempting to send report to channel: {channel}")
                await channel.send(embed=embed)
                print("Report sent successfully.")
            except discord.Forbidden:
                print("Error: The bot does not have permission to send messages in the 'reports' channel.")
            except Exception as e:
                print(f"Error: An unexpected error occurred: {e}")

            # Send a thank you message to the user who submitted the form
            await interaction.response.send_message(f"Thank you, {interaction.user.name}", ephemeral=True)

        
        async def on_error(self, interaction: discord.Interaction):
            ...


    @app_commands.command(name="report", description="Report a user")
    async def report(self, interaction: discord.Interaction):
        modal = self.ReportModal()
        modal.user = interaction.user
        await interaction.response.send_modal(modal)
    
async def setup(client: commands.Bot) -> None:
    await client.add_cog(Report(client))