import discord
import openai
from discord import app_commands
from discord.ext import commands
import config


client = commands.Bot(command_prefix="!", intents = discord.Intents.all())

@client.event
async def on_ready():
    print("Bot is up and ready!")
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands(s)")
    except Exception as e:
        print(e)

#bot says hello to the user / for test purposes
@client.tree.command(name="hello", description="Bot says hi to you")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}! This is GG study bot!",\
        ephemeral=True)

#say command(kinda like tts) / for test purposes
@client.tree.command(name="say", description="What should I say?")
async def say(interaction: discord.Interaction, thingtosay: str):
    await interaction.response.send_message(f"{interaction.user.name} said: `{thingtosay}`")

@client.tree.command(name="ask", description="Ask the bot a question")
async def ask(ctx, *, question: str):
    try:
        #set the OpenAI API key using the value from config.py
        openai.api_key = config.OPENAI_API_KEY

        # Use OpenAI to generate a response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Specify the ChatGPT model to use
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": question}
            ]
        )

        await ctx.send(response['choices'][0]['message']['content'])
    except Exception as e:
        await ctx.send(f"An error occurred: {e}")


client.run(config.TOKEN)
