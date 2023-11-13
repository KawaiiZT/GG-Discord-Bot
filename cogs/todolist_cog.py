import discord
from discord import app_commands
from discord.ext import commands

tasks = {}

class Todo(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    @app_commands.command(name='addtask', description='Add a task to your to-do list')
    async def add_task(self, interaction, task: str):
        if interaction.user.id not in tasks:
            tasks[interaction.user.id] = []
        tasks[interaction.user.id].append(task)
        await interaction.response.send_message(f'Task "{task}" added to your to-do list.')

    @app_commands.command(name='viewtasks', description='View your to-do list')
    async def view_tasks(self, interaction):
        user_tasks = tasks.get(interaction.user.id, [])
        if not user_tasks:
            await interaction.response.send_message('Your to-do list is empty.')
        else:
            task_list = '\n'.join(f'{index + 1}. {task}' for index, task in enumerate(user_tasks))
            await interaction.response.send_message(f'Your to-do list:\n{task_list}')

    @app_commands.command(name='removetask', description='Remove a task from your to-do list')
    async def remove_task(self, interaction, index: int):
        user_tasks = tasks.get(interaction.user.id, [])
        if 1 <= index <= len(user_tasks):
            removed_task = user_tasks.pop(index - 1)
            await interaction.response.send_message(f'Removed task "{removed_task}" from your to-do list.')
        else:
            await interaction.response.send_message('Invalid task index.')

    @app_commands.command(name='cleartasks', description='Clear your entire to-do list')
    async def clear_tasks(self, interaction):
        if interaction.user.id in tasks:
            tasks[interaction.user.id] = []
            await interaction.response.send_message('Cleared your entire to-do list.')
        else:
            await interaction.response.send_message('Your to-do list is already empty.')
    
    @app_commands.command(name='showtasks', description='Show your tasks list')
    async def show_tasks(self, interaction):
        user_tasks = tasks.get(interaction.user.id, [])
        if not user_tasks:
            await interaction.response.send_message('Your to-do list is empty.')
        else:
            task_list = '\n'.join(f'{index + 1}. {task}' for index, task in enumerate(user_tasks))
            await interaction.response.send_message(f'Your tasks list:\n{task_list}')
    
async def setup(client:commands.Bot) -> None:
    await client.add_cog(Todo(client))