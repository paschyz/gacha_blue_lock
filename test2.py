from typing import Optional

import discord
import os
import random
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
from discord import Interaction, app_commands, ui
from discord.ext import commands, tasks

from discord.ui import Button, View
load_dotenv()

discord_bot_key = os.getenv("DISCORD_BOT_KEY")
mongo_db_key = os.getenv("MONGO_DB_KEY")
guild_id = os.getenv("GUILD_ID")
client_mongo = MongoClient(
    mongo_db_key)
db = client_mongo["BlueLOCK"]
users_collection = db["users"]
cards_collection = db["cards"]
MY_GUILD = discord.Object(id=guild_id)  # replace with your guild id


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


class MyView(discord.ui.View):
    def __init__(self):
        super().__init__()

        self.button = discord.ui.Button(
            style=discord.ButtonStyle.green, label="Click me!")
        self.add_item(self.button)

    async def button_callback(self, interaction: discord.Interaction):
        await interaction.channel.send('Button clicked!', ephemeral=True)


def get_random_float():
    return round(random.uniform(0.00, 100.00), 2)


def get_card_rarity():
    randFloat = get_random_float()
    if randFloat <= 0.5:  # 0.5%
        print("legendary")
        return "legendary"
    if randFloat <= 5.5:  # 5%
        print("epic")
        return "epic"
    if randFloat <= 45.5:  # 40%
        print("rare")
        return "rare"
    else:
        print("common")
        return "common"


async def send_random_card(channel):
    card_name = roll_summon_category("common")
    await channel.send_message(card_name)


async def roll_summon_category(rarity):
    cardsQuery = cards_collection.find({"rarity": rarity})
    cards = list(cardsQuery)
    random_card = random.choice(cards)
    return (random_card["name"])


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


@client.tree.command()
async def random_card(interaction: discord.Interaction):
    card = await roll_summon_category(get_card_rarity())
    await interaction.response.send_message(card)


@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    channel = interaction.channel
    await channel.send("Hello, this is a message in a channel!")


@client.tree.command()
async def reset(interaction: discord.Interaction):
    """Resets everyone's summons !"""
    users_collection.update_many(
        {},
        {"$set": {"command_used": False}}
    )
    await interaction.response.send_message('Reset ! Everyone can summon now !')


@client.tree.command()
async def register(interaction: discord.Interaction):
    """Start collecting cards right now !"""
    doc = users_collection.find_one({"user_id": interaction.user.id})
    if doc is None:
        users_collection.insert_one(
            {"user_id": interaction.user.id, "username": interaction.user, "command_used": False, })
        await interaction.response.send_message('Register complete ! Have fun :)')
    else:
        await interaction.response.send_message('Already registered !')


@client.tree.command()
async def daily(interaction: discord.Interaction):
    """Daily summon !"""

    doc = users_collection.find_one({"user_id": interaction.user.id})
    if doc is None:
        await interaction.response.send_message('User not registered ! Use /register command')
    elif (doc['command_used'] == False):
        image_file = await send_random_image(interaction.response)
        users_collection.update_one(
            {"user_id": interaction.user.id},
            {"$set": {"command_used": True}}
        )
        users_collection.update_one(
            {"user_id": interaction.user.id},
            {"$push": {"dropped_images": image_file}}
        )
    else:
        await interaction.response.send_message('Command already used !')


@client.tree.command()
async def inventory(interaction: discord.Interaction):
    """Shows your player inventory!"""
    doc = users_collection.find_one({"user_id": interaction.user.id})

    embed = discord.Embed()
    for card in doc["dropped_images"]:
        embed.set_image(url="attachment://" + card)
        await interaction.channel.send(embed=embed, file=discord.File("images/banner1/" + card))


@client.tree.command()
async def embed(interaction: discord.Interaction):
    """embedMultipleImages test 4 imgs"""
    embed1 = discord.Embed().set_image(url="https://i.imgur.com/sCcejmy.png")
    embed2 = discord.Embed().set_image(url="https://i.imgur.com/TddUQWs.png")

    await interaction.response.send_message(embeds=[embed1, embed2])


client.run(
    discord_bot_key)
