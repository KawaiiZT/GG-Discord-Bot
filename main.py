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

@client.event
async def on_message(message):
    #check if  the message is from a user and not a bot
    if not message.author.client and client.user.mentioned_in(message):
        
        user_message = message.content.split(' ', 1)[1]
        
        response = 'Nothing yet!'

        if user_message.startwith('!ask'):
            question = message.content[5:] #remove "!ask" from the message content

            response = openai.ChatCompletion.create(
                medel="gpt-3.5-turbo", #Specify the ChatGPT model to use
                message=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "system", "content": question}
                ]
            )
        await message.channel.send(response['choices'][0]['message']['content'])
    await client.process_commands(message)

client.run(config.TOKEN)
client.run(config.OPENAI_API_KEY)