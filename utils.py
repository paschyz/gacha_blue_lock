import math
import random
import discord
from config import users_collection, cards_collection


from PIL import Image


class User:
    def __init__(self, discord_id, name, cards):
        self.discord_id = discord_id
        self.name = name
        self.cards = cards


class Ball:
    def __init__(self, position, emoji):
        self.position = position
        self.emoji = emoji
        self.hitbox = 30

    def move_right(self, player):
        self.position = (self.position[0] +
                         player.movement_speed, self.position[1])

    def move_left(self, player):
        self.position = (self.position[0] -
                         player.movement_speed, self.position[1])

    def move_up(self, player):
        self.position = (
            self.position[0], self.position[1] - player.movement_speed)

    def move_down(self, player):
        self.position = (
            self.position[0], self.position[1] + player.movement_speed)


class Player:
    def __init__(self, name, position, movement_speed, emoji):
        self.name = name
        self.position = position
        self.movement_speed = movement_speed
        self.emoji = emoji
        self.hitbox = 30

    def move_right(self):
        self.position = (self.position[0] +
                         self.movement_speed, self.position[1])

    def move_left(self):
        self.position = (self.position[0] -
                         self.movement_speed, self.position[1])

    def move_up(self):
        self.position = (self.position[0],
                         self.position[1] - self.movement_speed)

    def move_down(self):
        self.position = (self.position[0],
                         self.position[1] + self.movement_speed)


emoji = "C:\\Users\\k\\dev\\projects\\gacha_blue_lock\\img\\bachira_icon.png"
field = "C:\\Users\\k\\dev\\projects\\gacha_blue_lock\\img\\field.png"
img_result = "C:\\Users\\k\\dev\\projects\\gacha_blue_lock\\image_resultante.png"
emoji_rin = "C:\\Users\\k\\dev\\projects\\gacha_blue_lock\\img\\itoshi-r_icon.png"
ball = "img/ball.png"
blue_cursor = "img/blue_cursor.png"
red_cursor = "img/red_triangle.png"


def clear_field(field, img_result):
    img_fond = Image.open(field).convert("RGBA")
    img_fond.save(img_result)


def superposer_images(img_result,  field, players):
    clear_field(field, img_result)
    img_fond = Image.open(img_result).convert("RGBA")
    emoji_size = 75
    for i in players:
        emoji_paste = Image.open(i.emoji).convert(
            "RGBA").resize((emoji_size, emoji_size))
        position_to_substract = (int(emoji_size/2), int(emoji_size/2))

        final_position = (i.position[0] - position_to_substract[0],
                          i.position[1] - position_to_substract[1])
        cursor_paste = Image.open(red_cursor).convert("RGBA").resize((20, 20))

        img_fond.paste(
            cursor_paste, (i.position[0]-8, i.position[1]-63), cursor_paste)
        img_fond.paste(emoji_paste, final_position, emoji_paste)
        img_fond.save(img_result)


def get_pixels_on_line(point1, point2):
    """
    Returns a list of tuples representing all the pixels on a line between two points
    """
    x1, y1 = point1
    x2, y2 = point2
    dx = abs(x2 - x1)
    dy = abs(y2 - y1)
    sx = 1 if x1 < x2 else -1
    sy = 1 if y1 < y2 else -1
    err = dx - dy
    pixels = []
    while True:
        pixels.append((x1, y1))
        if x1 == x2 and y1 == y2:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x1 += sx
        if e2 < dx:
            err += dx
            y1 += sy
    return pixels


def get_pixels_on_circle(center, radius):
    """
    Returns a list of tuples representing all the pixels on a circle
    """
    pixels = []
    x0, y0 = center
    x = radius
    y = 0
    err = 0
    while x >= y:
        pixels.append((x0 + x, y0 + y))
        pixels.append((x0 + y, y0 + x))
        pixels.append((x0 - y, y0 + x))
        pixels.append((x0 - x, y0 + y))
        pixels.append((x0 - x, y0 - y))
        pixels.append((x0 - y, y0 - x))
        pixels.append((x0 + y, y0 - x))
        pixels.append((x0 + x, y0 - y))
        y += 1
        err += 1 + 2*y
        if 2*(err - x) + 1 > 0:
            x -= 1
            err += 1 - 2*x
    return pixels


def closest_player(players, position):
    closest_distance = math.inf
    closest_player = None

    for player in players:
        distance = math.sqrt(
            (player.position[0] - position[0]) ** 2 + (player.position[1] - position[1]) ** 2)
        if (distance < closest_distance and distance != 0):
            closest_distance = distance
            closest_player = player

    return closest_player


def put_ball(img_result,  position):
    img_fond = Image.open(img_result).convert("RGBA")
    ball_paste = Image.open(ball).convert("RGBA").resize((30, 30))
    img_fond.paste(ball_paste, position, ball_paste)
    img_fond.save(img_result)


def deplacer_joueur(position, img_result, emoji, field):
    superposer_images(img_result, emoji, field, position)


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
