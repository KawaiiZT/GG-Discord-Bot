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
            discord.SelectOption(label="To-Do List", emoji = "🗂"),
            discord.SelectOption(label="ChatGPT", emoji= "❓"),
            discord.SelectOption(label="Ticket", emoji= "✉"),
            discord.SelectOption(label="Welcome", emoji= "🚻"),
            discord.SelectOption(label="UserInfo", emoji= "🙍‍♂️"),
        ])
        
        async def my_callback(interaction):
            if select.values[0] == "Music":
                await interaction.response.send_message(f"You chose: {select.values[0]}")
                embed = discord.Embed(title=f"สวัสดีครับในนี้คือคำสั่งสำหรับหมวด Music ครับ 🎧",description="ดูคำสั่งด้านล่างได้เลย 👇", color=0x03a9f4)
                embed.add_field(name="เปิดเพลง ▶️", value="```/play [link]```", inline=True)
                embed.add_field(name="หยุดเพลงชั่วคราว ⏸️", value="```/pause```", inline=True)
                embed.add_field(name="เล่นเพลงต่อ ▶️", value="```/resume```", inline=True)
                embed.add_field(name="ให้ Bot เข้าเซิฟเวอร์ ✔️", value="```/join```", inline=True)
                embed.add_field(name="ค้นหาลิ้ง Youtube 🔗", value="```/ytsearch [query]```", inline=True)
                embed.add_field(name="ดูคิวเพลงทั้งหมด 📑 🔗", value="```/queue```", inline=True)
                embed.add_field(name="ข้ามไปอีกเพลงในคิว ▶️", value="```/skip```", inline=True)
                await interaction.followup.send(embed=embed)

            elif select.values[0] == "ChatGPT":
                await interaction.response.send_message(f"You chose: {select.values[0]}")
                embed = discord.Embed(title=f"สวัสดีครับในนี้คือคำสั่งสำหรับหมวด ChatGPT ครับ ❓", description="คำสั่งนี้ใช้เวลาในการ Process นานหน่อย กรุณารอด้วยนะครับ!", color=0x03a9f4)
                embed.add_field(name="ถามคำถาม Bot", value="``` /ask คำถามต่างๆ Eng/Thai ```", inline=True)
                await interaction.followup.send(embed=embed)
            
            elif select.values[0] == "To-Do List":
                await interaction.response.send_message(f"You chose: {select.values[0]}")
                embed = discord.Embed(title=f"สวัสดีครับในนี้คือคำสั่งสำหรับหมวด To-Do List ครับ 🗂",description="ดูคำสั่งด้านล่างได้เลย 👇", color=0x03a9f4)
                embed.add_field(name="เพิ่ม Task ✅", value="```/addtask [ชื่อ task]```", inline=True)
                embed.add_field(name="เอา Task ออก ❌", value="```/removetask [ชื่อ task]```", inline=True)
                embed.add_field(name="แสดง Task ทั้งหมด 📑", value="```/showtask```", inline=True)
                embed.add_field(name="ลบ Task ออกทั้งหมด 📃", value="```/cleartask```", inline=True)
                await interaction.followup.send(embed=embed)
            
            elif select.values[0] == "Ticket":
                await interaction.response.send_message(f"You chose: {select.values[0]}")
                embed = discord.Embed(title=f"สวัสดีครับในนี้คือคำสั่งสำหรับหมวด Ticket ครับ ✉", \
                    description="คำสั่งนี้ใช้ในการ Setup Ticket มีแค่ Role ที่มี Manage Message เท่านั้น ถึงจะสามารถใช้ได้ครับ",\
                    color=0x03a9f4)
                embed.add_field(name="Setup Ticket", value="```/ticketsetup```", inline=True)
                await interaction.followup.send(embed=embed)
                
            elif select.values[0] == "Welcome":
                await interaction.response.send_message(f"You chose: {select.values[0]}")
                embed = discord.Embed(title=f"สวัสดีครับในนี้คือคำสั่งสำหรับหมวด Welcome ครับ 🚻", \
                    description="คำสั่งนี้เป็นคำสั่งที่เป็น Default ของบอทอยู่แล้ว สามารถใช้ AutoRole ได้ โดยการใช้คือจะต้องมี Role Member ก่อนนะครับ",\
                    color=0x03a9f4)
                await interaction.followup.send(embed=embed)
            elif select.values[0] == "UserInfo":
                await interaction.response.send_message(f"You chose: {select.values[0]}")
                embed = discord.Embed(title=f"สวัสดีครับในนี้คือคำสั่งสำหรับหมวด UserInfo ครับ 🙍‍♂️", color=0x03a9f4)
                embed.add_field(name="เช็คข้อมูลส่วนตัว ✅", value="```/userinfo```", inline=True)
                await interaction.followup.send(embed=embed)
                
        select.callback = my_callback
        view = View()
        view.add_item(select)
        await interaction.response.send_message(f"Choose a category", view=view)

async def setup(client:commands.Bot) -> None:
    await client.add_cog(help(client))