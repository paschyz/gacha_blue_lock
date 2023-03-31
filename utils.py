import random
import discord
from config import users_collection, cards_collection


def get_random_float():
    return round(random.uniform(0.00, 100.00), 2)


async def verify_if_user_interaction_exists(interaction: discord.Interaction):
    doc = users_collection.find_one({"user_id": interaction.user.id})
    if doc is None:
        await interaction.response.send_message('{}, you are not registered !'.format(interaction.user.mention))
        return False
    else:
        return True


async def verify_if_user_interaction_not_exists(interaction: discord.Interaction):
    doc = users_collection.find_one({"user_id": interaction.user.id})
    if doc is not None:
        await interaction.response.send_message('{}, you are already registered !'.format(interaction.user.mention))
        return False
    else:
        return True


async def verify_if_user_mentionned_exists(interaction: discord.Interaction, user: discord.User):
    doc = users_collection.find_one({"user_id": user.id})
    if doc is None:
        await interaction.response.send_message('Mentionned user {} is not registered !'.format(user.mention))
        return False
    else:
        return True


async def verify_user_inventory(interaction: discord.Interaction):
    doc = users_collection.find_one({"user_id": interaction.user.id})
    if "dropped_images" in doc and len(doc["dropped_images"]) == 0:
        await interaction.response.send_message('{}, your inventory is empty !'.format(interaction.user.mention))
        return False
    else:
        return True


async def verify_summon_number_inferior_to_100(interaction: discord.Interaction, number: int):
    if number >= 100:
        await interaction.response.send_message('{}, you can\'t summon more than 100 cards at once ! (99 max)'.format(interaction.user.mention))
        return False
    else:
        return True


async def verify_summon_number_positive(interaction: discord.Interaction, number: int):
    if number <= 0:
        await interaction.response.send_message('{}, you can\'t summon 0 or less cards !'.format(interaction.user.mention))
        return False
    else:
        return True


async def verify_give_credits_number_positive(interaction: discord.Interaction, number: int):
    if number <= 0:
        await interaction.response.send_message('{}, you can\'t give 0 or less credits !'.format(interaction.user.mention))
        return False
    else:
        return True


async def verify_if_user_is_admin(interaction: discord.Interaction):
    required_role = discord.utils.get(
        interaction.guild.roles, name='Admin')
    if required_role in interaction.user.roles:
        return True
    else:
        await interaction.response.send_message('{} you are not an admin ! You are not authorized to use this command !'.format(interaction.user.mention))
        return False


async def verify_if_card_exists(interaction: discord.Interaction, card_name: str):
    doc = cards_collection.find_one({"name": card_name})
    if doc is None:
        await interaction.response.send_message('{}, this card does not exist !'.format(interaction.user.mention))
        return False
    else:
        return True


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
    card = {"name": random_card["name"], "rarity": random_card["rarity"].capitalize(),
            "card_image": random_card["card_image"], "color": get_color(rarity)}
    return card


def get_credit_rarity(rarity):
    if (rarity == "Legendary"):
        return 1000
    if (rarity == "Epic"):
        return 300
    if (rarity == "Rare"):
        return 25
    if (rarity == "Common"):
        return 10
    else:
        return 0


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
