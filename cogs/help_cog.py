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
                embed = discord.Embed(title=f"สวัสดีครับในนี้คือคำสั่งสำหรับหมวด Music ครับ🎧", color=0x03a9f4)
                embed.add_field(name="คำสั่งการใช้งาน 🎧Music🎧",  value="ดูตามคำสั่งด้านล่างได้เลย👇",inline=False)
                embed.add_field(name="เปิดเพลง▶️", value="```/play link```", inline=True)
                embed.add_field(name="หยุดเพลงชั่วคราว⏸️", value="```/pause```", inline=True)
                embed.add_field(name="เล่นเพลงต่อ▶️", value="```/resume```", inline=True)
                embed.add_field(name="👍ให้ Bot เข้าเซิฟเวอร์✔️", value="```/join```", inline=True)
                embed.add_field(name="👋ให้ Bot ออกเซิฟเวอร์❌", value="```/leave```", inline=True)
                await interaction.followup.send(embed=embed)

            elif select.values[0] == "ChatGPT":
                await interaction.response.send_message(f"You chose: {select.values[0]}")
                embed = discord.Embed(title=f"สวัสดีครับในนี้คือคำสั่งสำหรับหมวด ChatGPT ครับ❓", color=0x03a9f4)
                embed.add_field(name="ถามคำถาม Bot", value="```!ask คำถามต่างๆ Eng/Thai ```", inline=True)
                await interaction.followup.send(embed=embed)
            
            elif select.values[0] == "Attandance":
                await interaction.response.send_message(f"You chose: {select.values[0]}")
                embed = discord.Embed(title=f"สวัสดีครับในนี้คือคำสั่งสำหรับหมวด Attandance ครับ✅", color=0x03a9f4)
                embed.add_field(name="เช็คชื่อ", value="``` คำสั่งใส่ตรงนี้ ```", inline=True)
                await interaction.followup.send(embed=embed)


        select.callback = my_callback
        view = View()
        view.add_item(select)
        await interaction.response.send_message(f"Choose a category", view=view)

async def setup(client:commands.Bot) -> None:
    await client.add_cog(help(client))