from client import MyClient
from config import discord_bot_key, discord_bot_key_test, intents
from commands import setup_commands
# import pytz

# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.triggers.cron import CronTrigger
client = MyClient(intents=intents)
setup_commands(client)


async def daily_task():
    print("This task runs every day.")
    # Add your custom Python code here


# scheduler = AsyncIOScheduler()
# paris_tz = pytz.timezone('Europe/Paris')
# Schedule the task to run every day at 12:00 PM Paris time
# scheduler.add_job(daily_task, CronTrigger(
#     hour='23', minute='20', second='10', timezone=paris_tz))
# scheduler.start()
client.run(discord_bot_key_test)
