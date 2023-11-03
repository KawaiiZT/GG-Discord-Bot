import discord
import openai
import config

from discord.ext import commands

class gpt(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client    
    #ChatGPT Commandlines 
    @commands.command(name="ask")
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

async def setup(client:commands.Bot) -> None:
    await client.add_cog(gpt(client))