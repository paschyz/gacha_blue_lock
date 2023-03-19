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


@client.command(description="Says hello")
async def hello(ctx):
    await ctx.send('Hello, world!')


@client.command()
async def helpme(ctx):
    await ctx.send('Available commands:\n /register \n /card\n /inventory')


@client.command()
async def reset(ctx):
    users_collection.update_many(
        {},
        {"$set": {"command_used": False}}
    )
    await ctx.send('Reset ! Everyone can summon now !')


@client.command()
async def register(ctx):
    user_id = ctx.author.id
    username = str(ctx.author)
    doc = users_collection.find_one({"user_id": user_id})
    if doc is None:
        users_collection.insert_one(
            {"user_id": user_id, "username": username, "command_used": False, })
        await ctx.send('Register complete ! Have fun :)')
    else:
        await ctx.send('Already registered !')


@client.command()
async def summon(ctx):
    user_id = ctx.author.id
    username = str(ctx.author)
    doc = users_collection.find_one({"user_id": user_id})
    if doc is None:
        await ctx.send('User not registered ! Use /register command')
    elif (doc['command_used'] == False):
        image_file = await send_random_image(ctx.channel)
        users_collection.update_one(
            {"user_id": user_id},
            {"$set": {"command_used": True}}
        )
        users_collection.update_one(
            {"user_id": user_id},
            {"$push": {"dropped_images": image_file}}
        )
    else:
        await ctx.send('Command already used !')


@client.command()
async def inventory(ctx):
    user_id = ctx.author.id
    doc = users_collection.find_one({"user_id": user_id})
    for cards in doc["dropped_images"]:
        await ctx.send(file=discord.File("images/banner1/" + cards))


@client.command()
async def banner(ctx):
    image_files = os.listdir("images/banner1/")
    for cards in image_files:
        await ctx.send(file=discord.File("images/banner1/" + cards))


client.run(
    discord_bot_key)
