from typing import Optional

import discord
import os
import random
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
from discord import Interaction, app_commands, ui, ButtonStyle
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
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


class Carousel(View):
    def __init__(self, items):
        super().__init__()
        self.items = items
        self.current_index = 0

    @discord.ui.button(emoji="⬅️")
    async def button_left(self, interaction: Interaction, button: Button):
        self.current_index = (self.current_index - 1) % len(self.items)
        self.items[self.current_index].set_footer(
            text=f"{self.current_index + 1}/{len(self.items)}")
        await interaction.response.edit_message(embed=self.items[self.current_index])

    @discord.ui.button(emoji="➡️")
    async def button_right(self, interaction: Interaction, button: Button):
        self.current_index = (self.current_index + 1) % len(self.items)
        self.items[self.current_index].set_footer(
            text=f"{self.current_index + 1}/{len(self.items)}")
        await interaction.response.edit_message(embed=self.items[self.current_index])


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
    elif rarity == "epic":
        return discord.Colour.purple()
    elif rarity == "rare":
        return discord.Colour.blue()
    elif rarity == "common":
        return discord.Colour.green()
    else:
        return discord.Colour.default()


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print('Logged in as {0.user}!'.format(client))


@client.tree.command()
async def reset(interaction: discord.Interaction):
    """Resets everyone's daily summon ! Only available for the admins"""
    required_role = discord.utils.get(interaction.guild.roles, name='Admin')
    if required_role in interaction.user.roles:
        users_collection.update_many(
            {},
            {"$set": {"command_used": False}}
        )
        await interaction.response.send_message('Reset ! Everyone can summon now !')
    else:
        await interaction.response.send_message('You are not an admin ! You are not authorized to use this command !')


@client.tree.command()
async def register(interaction: discord.Interaction):
    """Conquer this world with your ego !"""
    doc = users_collection.find_one({"user_id": interaction.user.id})
    if doc is None:
        user_id = interaction.user.id
        user = str(interaction.user)
        users_collection.insert_one(
            {"user_id": user_id, "username": user, "command_used": False, })
        await interaction.response.send_message('Register complete ! Have fun :)')
    else:
        await interaction.response.send_message('Already registered !')


@client.tree.command(description="Daily summon !  |  Common (54.5%)   Rare (40%)   Epic (5%)   Legendary (0.5%)")
async def daily(interaction: discord.Interaction):

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
async def inventory(interaction: discord.Integration):
    """Shows your inventory !"""
    if verify_if_user_exists(interaction.user.id):
        if verify_user_inventory(interaction.user.id):
            items = []
            doc = users_collection.find_one({"user_id": interaction.user.id})

            # Fetch dropped_images and their ratings
            dropped_images_with_ratings = []
            for card in doc['dropped_images']:
                card_doc = cards_collection.find_one({"name": card})
                dropped_images_with_ratings.append((card, card_doc['rating']))

            # Sort dropped_images by rating
            sorted_dropped_images = sorted(
                dropped_images_with_ratings, key=lambda x: x[1], reverse=True)

            # Create embeds for the sorted dropped_images
            for card, rating in sorted_dropped_images:
                card_doc = cards_collection.find_one({"name": card})
                url_card = card_doc["card_image"]
                color = get_color(card_doc["rarity"])
                rarity = card_doc["name"]
                embed = discord.Embed(title=f"{interaction.user.name}'s inventory",
                                      description=rarity.capitalize(), color=color,
                                      url=url_card)
                embed.set_image(url=url_card)
                items.append(embed)
            carousel = Carousel(items)
            items[0].set_footer(
                text=f"{1}/{len(items)}")
            await interaction.response.send_message(embed=items[0], view=carousel)
        else:
            await interaction.response.send_message('No cards in inventory !')
    else:
        await interaction.response.send_message('User not registered ! Use /register command')


@client.tree.command()
async def reroll(interaction: discord.Interaction):
    """Reroll your account !    WARNING : This will delete your inventory and all you ressources !"""
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
    """Summon 3 players ! Only available for new users / rerolled users !"""
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
    """Show current banner !"""
    doc = cards_collection.find()
    embeds = []

    cards_with_rating = []

    for card in doc:
        cards_with_rating.append((card, card["rating"]))

    cards_with_rating = sorted(
        cards_with_rating, key=lambda x: x[1], reverse=True)

    for card in cards_with_rating:
        embed = discord.Embed()
        embed.title = card[0]["name"].capitalize()
        embed.set_image(url=card[0]["card_image"])
        embed.description = card[0]["rarity"].capitalize()
        embed.colour = get_color(card[0]["rarity"])
        embeds.append(embed)

    embeds[0].set_footer(
        text=f"{1}/{len(embeds)}")
    await interaction.response.send_message(embed=embeds[0], view=Carousel(embeds))


client.run(
    discord_bot_key)
