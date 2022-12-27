# db.users.update_one({"user_id": user_ids}, {"command_used": True})
import discord
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Access environment variables
discord_bot_key = os.getenv("DISCORD_BOT_KEY")

intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    if message.content.startswith('hi'):
        await message.channel.send('Hello!')


client.run(
    discord_bot_key)
