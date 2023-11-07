import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from discord.ext.commands import BadArgument

async def send_scheduled_message(channel, message):
    await channel.send(message)

@client.command()
async def schedule(ctx, ordinal, day, time, *, message):
    # ตรวจสอบให้แน่ใจว่าลำดับเป็นตัวเลขที่ถูกต้อง เช่น (13th, 14th, etc.)
    try:
        ordinal = int(ordinal)
    except ValueError:
        raise BadArgument("ใส่วันที่ผิด กรุณาเขียนเป็นวันที่เช่น 13, 14, และอื่นๆ.")

    #user ใส่วันของสัปดาห์และเวลา
    try:
        day = day.lower()  # Convert to lowercase ในกรณีที่เขียนตัวใหญ่มา
        days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        day_index = days_of_week.index(day)
        time_parts = time.split('.')
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        if day_index < 0 or hour < 0 or hour > 23 or minute < 0 or minute > 59:
            raise ValueError()
    except (ValueError, IndexError):
        await ctx.send("ใส่ข้อมูลวันไม่ถูกต้องกรุณา 'ordinal' เป็นวันที่ๆต้องการจะตั้งค่า (เช่น '13'), วันอะไรใน 'day' (เช่น 'monday'), และเวลาอะไร 'time' (ชั่วโมง.นาที) สำหรับการทำกำหนดการ.")
        return

    #คำนวณวันสำหรับการส่งข้อความ
    now = datetime.now()
    del_days = (day_index - now.weekday() + 7) % 7
    days_until_next_day = (7 * (ordinal - 1)) + del_days
    scheduled_date = now + timedelta(days=days_until_next_day, hours=hour - now.hour, minutes=minute - now.minute)
    scheduled_date = scheduled_date.replace(second=0, microsecond=0)

    #กำหนดเวลาการส่งข้อความ
    channel = ctx.channel
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_scheduled_message, 'date', run_date=scheduled_date, args=[channel, f"{ctx.author.mention}, {message}"])
    scheduler.start()

    await ctx.send(f"กำหนดการสำหรับวันที่ {ordinal} {day.capitalize()} ณ เวลา {hour:02}:{minute:02}. ของ {ctx.author.mention} จะถูกแจ้งเตือน")
