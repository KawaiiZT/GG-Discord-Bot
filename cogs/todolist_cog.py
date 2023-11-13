import discord
from discord import app_commands
from discord.ext import commands

tasks = {}

class Todo(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @app_commands.command(name='addtask', description='Add a task to your to-do list')
    async def add_task(self, interaction: discord.Interaction, task: str):
        if interaction.user.id not in tasks:
            tasks[interaction.user.id] = []
        tasks[interaction.user.id].append(task)
        add_response_embed = discord.Embed(title=f'Task `"{task}"` added to your to-do list. ✅', color=discord.Color.blue())
        await interaction.response.send_message(embed=add_response_embed, ephemeral=True)

    #remove task
    @app_commands.command(name='removetask', description='Remove a task from your to-do list')
    async def remove_task(self, interaction: discord.Interaction, index: int):
        remove_response_embed = discord.Embed(title='Removing your tasks...', color=discord.Color.green())
        await interaction.response.send_message(embed=remove_response_embed, ephemeral=True)
        user_tasks = tasks.get(interaction.user.id, [])
        if 1 <= index <= len(user_tasks):
            removed_task = user_tasks.pop(index - 1)
            embed = discord.Embed(
                title='Task Removed 🗑✅',
                description=f'Removed task "{removed_task}" from your to-do list. ✅',
                color=discord.Color.green()
            )
            await interaction.edit_original_response(embed=embed)
        else:
            embed = discord.Embed(
                title='Invalid Task Index ❌',
                description='Please provide a valid task index.',
                color=discord.Color.red()
            )
            await interaction.edit_original_response(embed=embed)


    #clear list
    @app_commands.command(name='cleartask', description='Clear your entire to-do list')
    async def clear_tasks(self, interaction:discord.Interaction):
        if interaction.user.id in tasks:
            tasks[interaction.user.id] = []
            embed = discord.Embed(
                title='To-Do List Cleared 🗑✅',
                description='Cleared your entire to-do list.',
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = discord.Embed(
                title='Empty To-Do List 📃',
                description='Your to-do list is already empty.',
                color=discord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

    #show all tasks list
    @app_commands.command(name='showtask', description='Show your to-do list')
    async def show_tasks(self, interaction: discord.Interaction):
        response_embed = discord.Embed(description="Getting your tasks...", color=discord.Color.blue())
        await interaction.response.send_message(embed=response_embed, ephemeral=True)
        user_tasks = tasks.get(interaction.user.id, [])
        if not user_tasks:
            embed = discord.Embed(
                title='To-Do List 📃',
                description='Your to-do list is empty.',
                color=discord.Color.blue()
            )
            await interaction.edit_original_response(embed=embed)
        else:
            embed = discord.Embed(
                title='Your To-Do List 📑',
                color=discord.Color.blue()
            )
            for index, task in enumerate(user_tasks):
                embed.add_field(name=f'Task {index + 1} 📂:', value=task, inline=False)
        await interaction.edit_original_response(embed=embed)
        
async def setup(client:commands.Bot) -> None:
    await client.add_cog(Todo(client))