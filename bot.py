import discord
import os
import random
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
from discord import Interaction, app_commands, ui
from discord.ext import commands, tasks
from discord.utils import MISSING
from discord.ui import Button, View

load_dotenv()

discord_bot_key = os.getenv("DISCORD_BOT_KEY")
mongo_db_key = os.getenv("MONGO_DB_KEY")
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
client_mongo = MongoClient(
    mongo_db_key)
db = client_mongo["BlueLOCK"]
users_collection = db["users"]
cards_collection = db["cards"]


class MyView(discord.ui.View):
    def __init__(self):
        super().__init__()

        self.button = discord.ui.Button(
            style=discord.ButtonStyle.green, label="Click me!")
        self.add_item(self.button)

    async def button_callback(self, interaction: discord.Interaction):
        await interaction.response.send_message("Button clicked!", ephemeral=True)


def get_random_float():
    return round(random.uniform(0.00, 100.00), 2)


def get_card_rarity():
    randFloat = get_random_float()
    if randFloat <= 0.5:  # 0.5%
        return "Legendary"
    if randFloat <= 5.5:  # 5%
        return "Epic"
    if randFloat <= 45.5:  # 40%
        return "Rare"
    else:
        return "Common"


async def send_random_image(channel):
    # Get a list of all files in the images directory
    image_files = os.listdir("images/banner1/")
    # Pick a random image file
    image_file = random.choice(image_files)
    # Send the image file to the channel
    await channel.send(file=discord.File("images/banner1/" + image_file))
    return image_file


async def send_random_card(channel):
    card_name = roll_summon_category("common")
    await channel.send(card_name)


async def roll_summon_category(rarity):
    cardsQuery = cards_collection.find({"rarity": rarity})
    cards = list(cards_collection)
    random_card = random.choice(cards)
    return (random_card["name"])


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.command()
async def random_card(ctx):
    send_random_card(ctx.channel)
    await ctx.send("Testing s!ummon")


@bot.command(description="Says hello")
async def hello(ctx):
    await ctx.send('Hello, world!')


@bot.command()
async def helpme(ctx):
    await ctx.send('Available commands:\n /register \n /card\n /inventory')


@bot.command()
async def reset(ctx):
    users_collection.update_many(
        {},
        {"$set": {"command_used": False}}
    )
    await ctx.send('Reset ! Everyone can summon now !')


@bot.command()
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


@bot.command()
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


@bot.command()
async def inventory(ctx):
    user_id = ctx.author.id
    doc = users_collection.find_one({"user_id": user_id})
    for cards in doc["dropped_images"]:
        await ctx.send(file=discord.File("images/banner1/" + cards))


@bot.command()
async def banner(ctx):
    image_files = os.listdir("images/banner1/")
    for cards in image_files:
        await ctx.send(file=discord.File("images/banner1/" + cards))


@bot.command()
async def send_button(ctx):
    view = MyView()
    await ctx.send("Testing buttons!", view=view)


bot.run(
    discord_bot_key)
