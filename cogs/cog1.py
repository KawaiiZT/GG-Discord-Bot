import discord
from discord.ext import commands
from discord import app_commands
import gspread
from oauth2client.service_account import ServiceAccountCredentials

class cog1(commands.Cog):
    def __init__(self, client: commands.Bot) -> None:
        self.client = client
        self.scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive.file','https://www.googleapis.com/auth/drive']
        self.creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', self.scope)
        self.client_gs = gspread.authorize(self.creds)
        self.sheet = self.client_gs.open('attendance_demo').sheet1  # Open the spreadhseet

    @app_commands.command(name="checkin", description="Check in for attendance")
    async def checkin(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        user_name = interaction.user.name
        row = [user_id, user_name]
        self.sheet.append_row(row)  # Append a row to the sheet
        await interaction.response.send_message(f"Attendance checked in for {interaction.user.mention}!", ephemeral=True)

async def setup(client:commands.Bot) -> None:
    await client.add_cog(cog1(client))
