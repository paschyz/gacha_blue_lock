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
client = discord.Client(command_prefix='/', intents=intents)
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
    return image_file


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.event
async def on_message(message):
    user_id = message.author.id
    username = str(message.author)

    if message.content.startswith('/help'):
        await message.channel.send('Available commands:\n /register \n /card\n /inventory')

    if message.content.startswith('/reset'):
        doc = users_collection.find()
        users_collection.update_many(
            {},
            {"$set": {"command_used": False}}
        )
        await message.channel.send('Reset ! Everyone can summon now !')

    if message.content.startswith('/register'):
        doc = users_collection.find_one({"user_id": user_id})
        if doc is None:
            users_collection.insert_one(
                {"user_id": user_id, "username": username, "command_used": False, })
            await message.channel.send('Register complete ! Have fun :)')
        else:
            await message.channel.send('Already registered !')

    if message.content.startswith('/tt'):
        await message.channel.send(username)

    if message.content.startswith('/card'):
        doc = users_collection.find_one({"user_id": user_id})
        if doc is None:
            await message.channel.send('User not registered ! Use /register command')
        elif (doc['command_used'] == False):
            image_file = await send_random_image(message.channel)
            users_collection.update_one(
                {"user_id": user_id},
                {"$set": {"command_used": True}}
            )
            users_collection.update_one(
                {"user_id": user_id},
                {"$push": {"dropped_images": image_file}}
            )
        else:
            await message.channel.send('Command already used !')

    if message.content.startswith('/inventory'):
        doc = users_collection.find_one({"user_id": user_id})
        for cards in doc["dropped_images"]:
            await message.channel.send(file=discord.File("img/cards/" + cards))

client.run(
    discord_bot_key)
