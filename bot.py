# db.users.update_one({"user_id": user_ids}, {"command_used": True})
import discord
import os
import random
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
from discord import Interaction, app_commands, ui
from discord.ext import commands, tasks
from discord.utils import MISSING

load_dotenv()

discord_bot_key = os.getenv("DISCORD_BOT_KEY")
mongo_db_key = os.getenv("MONGO_DB_KEY")
intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='!', intents=intents)
client_mongo = MongoClient(
    mongo_db_key)
db = client_mongo["BlueLOCK"]
users_collection = db["users"]


async def send_random_image(channel):
    # Get a list of all files in the images directory
    image_files = os.listdir("images/banner1/")
    # Pick a random image file
    image_file = random.choice(image_files)
    # Send the image file to the channel
    await channel.send(file=discord.File("images/banner1/" + image_file))
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

    if message.content.startswith('/create'):
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

    if message.content.startswith('/banner'):
        image_files = os.listdir("images/banner1/")
        for cards in image_files:
            await message.channel.send(file=discord.File("images/banner1/" + cards))

    # @client.command(description='TEST')
    # async def mission(ctx):
    #     # Your implementation of the mission method goes here
    #     await ctx.send('This is a test')
        # Define the carousel message
    # Define the carousel message
message = discord.Embed(title="Carousel Message",
                        description="Here's an example carousel message:")
message.set_image(url="https://example.com/carousel.jpg")
message.set_footer(text="Footer text")

# Define the carousel items
items = [
    {"name": "Card 1", "description": "Description for Card 1",
        "image_url": "https://example.com/card1.jpg", "url": "https://example.com/card1"},
    {"name": "Card 2", "description": "Description for Card 2",
        "image_url": "https://example.com/card2.jpg", "url": "https://example.com/card2"},
    {"name": "Card 3", "description": "Description for Card 3",
        "image_url": "https://example.com/card3.jpg", "url": "https://example.com/card3"}
]

# Add the carousel items to the message
for item in items:
    card = discord.Embed(title=item["name"], description=item["description"])
    card.set_image(url=item["image_url"])
    card.add_field(name="Link", value=item["url"])
    message.add_field(name="\u200b", value="\u200b", inline=False)
    message.add_field(name="\u200b", value=card, inline=False)

# Define the command to send the message


@client.command()
async def send_carousel(ctx):
    await ctx.send(embed=message)


client.run(
    discord_bot_key)
