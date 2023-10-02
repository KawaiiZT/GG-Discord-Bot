import discord
import openai
import config
import os


from discord.utils import get
from discord import app_commands
from discord.ext import commands
from keep_alive import keep_alive
from music_cog import music_cog

client = commands.Bot(command_prefix="!", intents = discord.Intents.all())
client.remove_command('help')

@client.event
async def on_ready():
    #this line can change of what bot status it doing rightnow ex."Playing helping my teammate now"
    await client.change_presence(status=discord.Status.online, activity=discord.Game('helping my teammate now'))
    print("Bot is up and ready!")
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands(s)")
    except Exception as e:
        print(e)
    
    await client.add_cog(music_cog(client))
 

@client.event
async def onready():
    for guild in client.guilds:
        for channel in guild.txt_channels:
            if str(channel).strip() == "verify":   #verify = ห้องที่จะใช้
                global verify_channel_id
                verify_channel_id = channel.id
                break

@client.event
async def on_raw_react_add(reaction):
    if reaction.channel_id  == verify_channel_id:
        if str(reaction.emoji) == "":
            verified_role = get(reaction.member.guild.roles, name = "role")
            await reaction.member.add_roles(verified_role)
        elif str(reaction.emoji) == "":
            verified_role = get(reaction.member.guild.roles, name = "role")
            await reaction.member.add_roles(verified_role)

#bot says hello to the user / for test purposes
@client.tree.command(name="hello", description="Bot says hi to you")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(f"Hey {interaction.user.mention}! This is GG study bot!",\
        ephemeral=True)

#say command(kinda like tts) / for test purposes
@client.tree.command(name="say", description="What should I say?")
async def say(interaction: discord.Interaction, thingtosay: str):
    await interaction.response.send_message(f"{interaction.user.name} said: `{thingtosay}`")

#ChatGPT Commandlines 
@client.command(name="ask", description="Ask the bot a question")
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

keep_alive()
client.run(config.TOKEN)
