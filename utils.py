import random
import discord
from config import users_collection, cards_collection


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
