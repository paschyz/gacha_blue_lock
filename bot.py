# db.users.update_one({"user_id": user_ids}, {"command_used": True})
import discord
import os
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
# Load environment variables from .env file
load_dotenv()

# Access environment variables
discord_bot_key = os.getenv("DISCORD_BOT_KEY")
mongo_db_key = os.getenv("MONGO_DB_KEY")

intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)
client_mongo = MongoClient(
    mongo_db_key)
db = client_mongo["BlueLOCK"]
users_collection = db["users"]


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    user_id = message.author.id
    if message.content.startswith('hi'):
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"command_used": True}}
        )
        await message.channel.send('Hello!')


client.run(
    discord_bot_key)
