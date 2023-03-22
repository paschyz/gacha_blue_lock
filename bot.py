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


class MyView(View):
    @discord.ui.button(label="Click me")
    async def on_button_click(self, button: Button, interaction: Interaction):
        await interaction.response.send_message("Button clicked!")


def get_random_float():
    return round(random.uniform(0.00, 100.00), 2)


def verify_if_user_exists(user_id):
    doc = users_collection.find_one({"user_id": user_id})
    if doc is None:
        return False
    else:
        return True


def verify_user_inventory(user_id):
    doc = users_collection.find_one({"user_id": user_id})
    if "dropped_images" in doc and len(doc["dropped_images"]) > 0:
        return True
    else:
        return False


def get_card_rarity():
    randFloat = get_random_float()
    if randFloat <= 0.5:  # 0.5%
        return "legendary"
    if randFloat <= 5.5:  # 5%
        return "epic"
    if randFloat <= 45.5:  # 40%
        return "rare"
    else:  # 54.5%
        return "common"


async def send_random_card(channel):
    card_name = roll_summon_category("common")
    await channel.send_message(card_name)


async def roll_summon_category(rarity):
    cardsQuery = cards_collection.find({"rarity": rarity})
    cards = list(cardsQuery)
    random_card = random.choice(cards)
    get_color(rarity)
    card = {"name": random_card["name"].capitalize(), "rarity": random_card["rarity"].capitalize(),
            "card_image": random_card["card_image"], "color": get_color(rarity)}
    return card


def get_color(rarity):
    if rarity == "legendary":
        return discord.Colour.gold()
    if rarity == "epic":
        return discord.Colour.purple()
    if rarity == "rare":
        return discord.Colour.blue()
    if rarity == "common":
        return discord.Colour.green()


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print('Logged in as {0.user}!'.format(client))


@client.tree.command()
async def button_test(interaction: discord.Interaction):
    """Test a button"""
    view = MyView()
    # @client.tree.command()
    await interaction.response.send_message("Testing a button!", view=view)


@client.tree.command()
async def reset(interaction: discord.Interaction):
    """Resets everyone's summons !"""
    if (interaction.user.id == 314809676447350785):
        users_collection.update_many(
            {},
            {"$set": {"command_used": False}}
        )
        await interaction.response.send_message('Reset ! Everyone can summon now !')
    else:
        await interaction.response.send_message('You are not authorized to use this command !')


@client.tree.command()
async def register(interaction: discord.Interaction):
    """Start collecting cards right now !"""
    doc = users_collection.find_one({"user_id": interaction.user.id})
    if doc is None:
        user_id = interaction.user.id
        user = str(interaction.user)
        users_collection.insert_one(
            {"user_id": user_id, "username": user, "command_used": False, })
        await interaction.response.send_message('Register complete ! Have fun :)')
    else:
        await interaction.response.send_message('Already registered !')


@client.tree.command()
async def daily(interaction: discord.Interaction):
    """Daily summon ! \n Common (54.5%) \n Rare (40%) \n Epic (5%) \n Legendary (0.5%)"""

    doc = users_collection.find_one({"user_id": interaction.user.id})
    if doc is None:
        await interaction.response.send_message('User not registered ! Use /register command')
    elif (verify_user_inventory(interaction.user.id)):
        if (doc['command_used'] == False):
            getcard = await roll_summon_category(get_card_rarity())
            embed = discord.Embed(colour=discord.Colour.red())
            embed.set_image(url=getcard["card_image"])
            embed.description = getcard["rarity"]
            embed.title = getcard["name"]
            embed.colour = getcard["color"]
            await interaction.response.send_message(embed=embed)
            users_collection.update_one(
                {"user_id": interaction.user.id},
                {"$set": {"command_used": True}}
            )
            users_collection.update_one(
                {"user_id": interaction.user.id},
                {"$push": {"dropped_images": getcard["name"].lower()}}
            )
        else:
            await interaction.response.send_message('Command already used !')
    else:
        await interaction.response.send_message('Inventory Empty ! Use /multi command to get more cards !')


@client.tree.command()
async def inventory(interaction: discord.Interaction):
    """Shows your inventory!"""
    if (verify_if_user_exists(interaction.user.id)):
        if (verify_user_inventory(interaction.user.id)):
            doc = users_collection.find_one({"user_id": interaction.user.id})
            embed = discord.Embed()
            for card in doc['dropped_images']:
                embed.title = interaction.user.name + "'s inventory"
                url_card = cards_collection.find_one({"name": card})[
                    "card_image"]
                color = get_color(cards_collection.find_one(
                    {"name": card})["rarity"])
                rarity = cards_collection.find_one({"name": card})["rarity"]
                embed.set_image(url=url_card)
                embed.description = rarity.capitalize()
                embed.colour = color
                await interaction.channel.send(embed=embed)
        else:
            await interaction.response.send_message('No cards in inventory !')
    else:
        await interaction.response.send_message('User not registered ! Use /register command')


@client.tree.command()
async def reroll(interaction: discord.Interaction):
    """Reroll all your summons !"""
    if (verify_if_user_exists(interaction.user.id)):
        users_collection.update_one(
            {"user_id": interaction.user.id}, {"$set": {"command_used": False}})
        users_collection.update_one(
            {"user_id": interaction.user.id}, {"$set": {"dropped_images": []}})
        await interaction.response.send_message('Reroll complete !')
    else:
        await interaction.response.send_message('User not registered ! Use /register command')


@client.tree.command()
async def multi(interaction: discord.Interaction):
    """Multi-summon right now !"""
    if (verify_if_user_exists(interaction.user.id)):
        if (verify_user_inventory(interaction.user.id)):
            await interaction.response.send_message('You already have cards in your inventory ! Use /reroll command to reroll your summons')
        else:
            for i in range(3):
                getcard = await roll_summon_category(get_card_rarity())
                embed = discord.Embed(colour=discord.Colour.red())
                embed.set_image(url=getcard["card_image"])
                embed.description = getcard["rarity"]
                embed.title = getcard["name"]
                embed.colour = getcard["color"]
                await interaction.channel.send(embed=embed)
                users_collection.update_one(
                    {"user_id": interaction.user.id},
                    {"$push": {"dropped_images": getcard["name"].lower()}}
                )
    else:
        await interaction.response.send_message('User not registered ! Use /register command')


@client.tree.command()
async def banner(interaction: discord.Interaction):
    """Show banner !"""
    doc = cards_collection.find()
    for card in doc:
        embed = discord.Embed()
        embed.title = card["name"].capitalize()
        embed.set_image(url=card["card_image"])
        embed.description = card["rarity"].capitalize()
        embed.colour = get_color(card["rarity"])
        await interaction.channel.send(embed=embed)

# @client.tree.command()
# async def embed(interaction: discord.Interaction):
#     """embedMultipleImages test 4 imgs"""
#     embed1 = discord.Embed().set_image(url="https://i.imgur.com/sCcejmy.png")
#     embed2 = discord.Embed().set_image(url="https://i.imgur.com/TddUQWs.png")

#     await interaction.response.send_message(embeds=[embed1, embed2])


client.run(
    discord_bot_key)
