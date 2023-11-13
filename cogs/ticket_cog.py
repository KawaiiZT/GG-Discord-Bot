from typing import Optional
from discord import app_commands, ui
from discord.ext import commands
import discord
from discord.interactions import Interaction
import datetime

class Tickets(commands.Cog):
    def __init__(self, client: commands.Bot):
        self.client = client

    async def create_ticket_setup(self, interaction: Interaction):
        categories = ["General Support", "Bug Support", "Feature Request", "Code Question"]

        # Check if the channel already exists
        channel_name = "ticket-submission"
        channel = discord.utils.get(interaction.guild.channels, name=channel_name)
        if not channel:
            staff = discord.utils.get(interaction.guild.roles, name="Staff")
            overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
                          staff: discord.PermissionOverwrite(view_channel=True, send_messages=True)}
            channel = await interaction.guild.create_text_channel(name=channel_name, overwrites=overwrites)

            for category_name in categories:
                # Check if the category already exists
                category = discord.utils.get(interaction.guild.categories, name=category_name)
                if not category:
                    category = await interaction.guild.create_category(category_name)

            embed = discord.Embed(title="Ticket Submission", description=f"Please select your ticket category down below for {category_name}.", color=discord.Color.greyple())
            await channel.send(embed=embed, view=DropDown())

        await interaction.response.send_message("Successfully set up the ticket system! Make sure you already have the `Staff` roles in the server before you use this function.", ephemeral=True)

    @app_commands.command(name="ticketsetup", description="Sends the ticket prompt message.")
    @app_commands.default_permissions(manage_messages=True)
    async def ticketsetup(self, interaction: Interaction):
        await self.create_ticket_setup(interaction)
        
ticket_numbers = {}
        
class DropDown(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)
        
        
    async def create_ticket(self, interaction: discord.Interaction, selection: str):
        global ticket_numbers  # Reference the global variable
        #How it works?
        #get ticket "description"
        ticket_descriptions = {"General Support": "Our staff team will be with you shortly",
                               "Bug Support": "Please do not abuse this bug!",
                               "Feature Request": "",
                               "Code Question": "",}
        selected_description = ticket_descriptions.get(selection, "")
        #create the overwrites
        staff = discord.utils.get(interaction.guild.roles, name="Staff")
        channel_overwrites = {interaction.user: discord.PermissionOverwrite(view_channel=True, send_messages=False),
                              staff: discord.PermissionOverwrite(view_channel=True, send_messages=True),
                              interaction.guild.default_role: discord.PermissionOverwrite(view_channel=False)}
        #make the channel
        ticket_number = ticket_numbers.get(selection, 0) + 1
        ticket_numbers[selection] = ticket_number
        formatted_number = f"{ticket_number:04d}"
        category = discord.utils.get(interaction.guild.channels, name=selection)
        channel = await interaction.guild.create_text_channel(name=f"{interaction.user.name}-{formatted_number}", overwrites=channel_overwrites, category=category)
        #send/delete tag
        tag = await channel.send(staff.mention)
        await tag.delete()
        #respond to the user
        await interaction.followup.send(content=f"Successfully created your ticket! {channel.mention}", ephemeral=True)
        #send the ticket message in the ticket
        embed = discord.Embed(description=f"Hey {interaction.user.mention}!\n"
                                            ""
                                            "You have created a new ticket\n"
                                            f"**Type:** {selection}\n \n"
                                            ""
                                            f"{selected_description}\n", color=discord.Color.blurple(), timestamp=datetime.datetime.now())
        
        await channel.send(embed=embed, view=EnterInfo(str(selection)))
        
        
    @discord.ui.select(options= [discord.SelectOption(label="General Support"),
                                discord.SelectOption(label="Bug Support"),
                                discord.SelectOption(label="Feature Request"),
                                discord.SelectOption(label="Code Question")],
                    placeholder='Choose a category for your ticket',
                    custom_id="dropdown")
    async def selectmenu(self, interaction: discord.Interaction, select: ui.select):
        await interaction.response.defer()
        await interaction.message.edit(view=DropDown())
        await self.create_ticket(interaction, select.values[0])
        
        
class EnterInfo(discord.ui.View):
    def __init__(self, ticket_type: str) -> None:
        self.ticket_type = ticket_type
        super().__init__(timeout=None)
            
    @discord.ui.button(label="Enter Information", style=discord.ButtonStyle.green, custom_id="enter_information_button")
    async def enterInfoButton(self, interaction: discord.Interaction, Button: discord.ui.Button):
        await interaction.response.send_modal(PopUp(self.ticket_type))
    
    @discord.ui.button(label="Close Ticket", style=discord.ButtonStyle.red, custom_id="close_ticket_button")
    async def closeTicketButton(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Get the channel from the interaction
        channel = interaction.channel
    
        # Check if the user has the necessary permissions to delete the channel
        if interaction.user.guild_permissions.manage_channels:
            # Delete the channel
            await channel.delete()
            await interaction.response.send_message("Ticket closed successfully.", ephemeral=True)
        else:
            # If the user doesn't have the necessary permissions, notify them
            await interaction.response.send_message("You do not have the required permissions to close this ticket.", ephemeral=True)
    
class PopUp(ui.Modal):
    def __init__(self, ticket_type: str) -> None:
        self.ticket_type = ticket_type
        super().__init__(title="Ticket Information", timeout=None, custom_id="Modal")
        

        self.add_item(ui.TextInput(label="What is your name?", placeholder="og. Cherrine", style=discord.TextStyle.short))
            
        if self.ticket_type == "General Support":
            self.add_item(ui.TextInput(label="What is your issue", placeholder="og. I don't know how this code not working, etc.", style=discord.TextStyle.short))
            self.add_item(ui.TextInput(label="Can you specify for more detail?", placeholder="", style=discord.TextStyle.long))
        
        elif self.ticket_type == "Bug Support":
            self.add_item(ui.TextInput(label="Please explain the bug in detail", placeholder="If you have a video, you can paste the video link here.", style=discord.TextStyle.long))    
        
        elif self.ticket_type == "Feature Request":
            self.add_item(ui.TextInput(label="What is your feature request and why?", placeholder="", style=discord.TextStyle.long))
        
        elif self.ticket_type == "Code Question":
            self.add_item(ui.TextInput(label="What is the question on your code?", placeholder="Please use pastebin website to paste your code if you are gonna include it.", style=discord.TextStyle.long))
    
    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        #place information in embed
        embed = interaction.message.embeds[0]
        description = embed.description
        split_description = description.split("\n \n")
        
        for item in self.children:
            split_description.insert(2, f"**{item.label}**\n{item.value}")

        embed.description = "\n \n".join(split_description)

        await interaction.message.edit(view=None, embed=embed)
        #edit the channel permissions (allow member to send messages)
        permissions = interaction.channel.overwrites_for(interaction.user)
        permissions.send_messages = True
        await interaction.channel.set_permissions(target=interaction.user, overwrite=permissions)
    

async def setup(client:commands.Bot) -> None:
    await client.add_cog(Tickets(client))