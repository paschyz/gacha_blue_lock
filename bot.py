# db.users.update_one({"user_id": user_ids}, {"command_used": True})
import discord
import os
import random
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient

load_dotenv()

discord_bot_key = os.getenv("DISCORD_BOT_KEY")
mongo_db_key = os.getenv("MONGO_DB_KEY")
intents = discord.Intents.all()
client = discord.Client(command_prefix='!', intents=intents)
client_mongo = MongoClient(
    mongo_db_key)
db = client_mongo["BlueLOCK"]
users_collection = db["users"]


async def send_random_image(channel):
    # Get a list of all files in the images directory
    image_files = os.listdir("img/cards/")
    # Pick a random image file
    image_file = random.choice(image_files)
    # Send the image file to the channel
    await channel.send(file=discord.File("img/cards/" + image_file))


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    user_id = message.author.id

    if message.content.startswith('hi'):
        cursor = users_collection.find({"user_id": user_id})
        # Build a string with the results of the query
        result_string = "Query results:\n"

        for doc in cursor:
            result_string += f"{doc['user_id']} - {doc['command_used']}\n"
            if (doc['command_used'] == False):
                await send_random_image(message.channel)

        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"command_used": True}}
        )

    if message.content.startswith('ok'):
        await send_random_image(message.channel)

client.run(
    discord_bot_key)
