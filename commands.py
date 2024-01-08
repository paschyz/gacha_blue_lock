import asyncio
from config import mongo_db_key, admin_id
from utils import *
from carousel import Carousel, Game
from client import MyClient
from pymongo import MongoClient
from typing import Optional
from asyncio import sleep, wait
client_mongo = MongoClient(mongo_db_key)
db = client_mongo["BlueLOCK"]
users_collection = db["users"]
cards_collection = db["cards"]

cages_top = "------------------------------------\ ............................/ ------------------------------------"
columns = "|                              |                              |                              |                              |                              |"
rows = "-----------------------------------------------------------------------------------------------"
cages_bottom = "------------------------------------ /............................\ ------------------------------------"


def create_and_display_grid(player_positions):
    width = 5
    height = 5
    grid = [["[ ]" for _ in range(width)] for _ in range(height)]

    for player_name, position in player_positions.items():
        x, y = position
        grid[y][x] = f"[{player_name}]"

    grid_str = "\n".join("".join(row) for row in grid)
    return grid_str


def setup_commands(client: MyClient):

    @client.event
    async def on_ready():
        print('Logged in as {0.user}!'.format(client))

    @client.tree.command(description="Shows the list of available commands and their descriptions.")
    async def help(interaction: discord.Interaction):
        commands = {
            "register": "Conquer this world with your ego !",
            "balance": "Shows your *EgoCoins*",
            "inventory": "Shows your inventory",
            "summon": "Summon cards ! \n Costs **100** *EgoCoins* per summon \n Common *(54.5%)* | Rare *(40%)* | Epic *(5%)* | Legendary *(0.5%)*",
            "banner": "Shows current banner",
            "reroll": "**[WARNING : This will delete all your cards/ressources.]** \n You will have **400 ** *EgoCoins* on reroll",
            "give_credits": "**[ADMIN ONLY]** Give credits !",
            "give_card": "**[ADMIN ONLY]** Give cards !",
        }
        embed = discord.Embed(
            title="Help", description="Available commands:", color=discord.Colour.blue())

        for command, description in commands.items():
            embed.add_field(name=f"/{command}",
                            value=description, inline=False)

        await interaction.response.send_message(embed=embed)

    @client.tree.command(description="Conquer this world with your ego !")
    async def register(interaction: discord.Interaction):
        if not await verify_if_user_interaction_not_exists(interaction):
            return
        user_id = interaction.user.id
        user = str(interaction.user)
        users_collection.insert_one(
            {"user_id": user_id, "username": user, "ego_coins": 400, "dropped_images": []})
        await interaction.response.send_message('Register complete {}, Welcome !'.format(interaction.user.mention))

    @client.tree.command(description="Shows your EgoCoins")
    async def balance(interaction: discord.Interaction):
        if not await verify_if_user_interaction_exists(interaction):
            return
        doc = users_collection.find_one({"user_id": interaction.user.id})
        await interaction.response.send_message('{}, you have **{}** *EgoCoins* !'.format(interaction.user.mention, doc['ego_coins']))

    @client.tree.command(description="Shows your inventory")
    async def inventory(interaction: discord.Interaction):
        if not await verify_if_user_interaction_exists(interaction):
            return
        if not await verify_user_inventory(interaction):
            return
        items = []
        doc = users_collection.find_one(
            {"user_id": interaction.user.id})

        # Fetch dropped_images and their ratings
        dropped_images_with_ratings = []
        for card in doc['dropped_images']:
            card_doc = cards_collection.find_one({"name": card})
            dropped_images_with_ratings.append(
                (card, card_doc['rating']))

         Sort dropped_images by rating
        sorted_dropped_images = sorted(
            dropped_images_with_ratings, key=lambda x: x[1], reverse=True)

        # Create embeds for the sorted dropped_images
        for card, rating in sorted_dropped_images:
            card_doc = cards_collection.find_one({"name": card})
            url_card = card_doc["card_image"]
            color = get_color(card_doc["rarity"])
            rarity = card_doc["name"]
            embed = discord.Embed(title=f"{interaction.user.name}'s inventory",
                                  color=color,
                                  )
            embed.set_image(url=url_card)
            items.append(embed)
        carousel = Carousel(items)
        items[0].set_footer(
            text=f"{1}/{len(items)}")
        await interaction.response.send_message(embed=items[0], view=carousel)

    @client.tree.command(description="Summon cards ! [100 EgoCoins/summon] Common (54.5%) | Rare (40%) | Epic (5%) | Legendary (0.5%)")
    async def summon(interaction: discord.Interaction, number_of_summons: int):
        if not await verify_if_user_interaction_exists(interaction):
            return
        if not await verify_summon_number_inferior_to_100(interaction, number_of_summons):
            return
        if not await verify_summon_number_positive(interaction, number_of_summons):
            return
        doc = users_collection.find_one({"user_id": interaction.user.id})
        ego_coins = doc["ego_coins"]
        items = []
        credits_to_refund = 0
        if (ego_coins >= number_of_summons*100):

            for i in range(number_of_summons):
                doc = users_collection.find_one(
                    {"user_id": interaction.user.id})  # Refresh doc
                getcard = await roll_summon_category(get_card_rarity())
                embed = discord.Embed()
                embed.set_image(url=getcard["card_image"])
                embed.title = "{}'s summon n°{}".format(
                    interaction.user.name, i+1)
                embed.set_footer(
                    text="{}/{}".format(i+1, number_of_summons))
                embed.colour = getcard["color"]
                embed.description = "New player **{}** dropped ! ({})".format(
                    getcard["name"].capitalize(), getcard["rarity"])
                if (getcard["name"]) in doc['dropped_images']:
                    credits_refunded = get_credit_rarity(getcard["rarity"])
                    credits_to_refund += credits_refunded
                    embed.description = "**{}** *EgoCoins* refunded. (Duplicate) ".format(
                        credits_refunded)
                else:
                    users_collection.update_one(
                        {"user_id": interaction.user.id},
                        {"$push": {"dropped_images": getcard["name"].lower()}}
                    )
                items.append(embed)
            new_ego_coins = ego_coins - number_of_summons*100 + credits_to_refund
            users_collection.update_one({"user_id": interaction.user.id}, {
                                        "$set": {"ego_coins": new_ego_coins}})
            await interaction.response.send_message(embed=items[0], view=Carousel(items))
            await interaction.channel.send("**{}** *EgoCoins used*.".format(number_of_summons*100))
            await interaction.channel.send("**{}** *EgoCoins refunded*.".format(credits_to_refund))
            await interaction.channel.send("{}, You have now **{}** *EgoCoins left* !".format(interaction.user.mention, new_ego_coins))
        else:
            await interaction.response.send_message('Not enough credits. You have **{}** *EgoCoins* !'.format(doc['ego_coins']))

    @client.tree.command(description="View and edit your team")
    async def team(interaction: discord.Interaction):
        if not await verify_if_user_interaction_exists(interaction):
            return
        if not await verify_user_inventory(interaction):
            return
        doc = users_collection.find_one({"user_id": interaction.user.id})
        items = []
        for card in doc["team"]:
            card_doc = cards_collection.find_one({"name": card})
            url_card = card_doc["card_image"]
            color = get_color(card_doc["rarity"])
            rarity = card_doc["name"]
            embed = discord.Embed(title=f"{interaction.user.name}'s team",
                                  color=color,
                                  )
            embed.set_image(url=url_card)
            items.append(embed)
        items[0].set_footer(text=f"{1}/{len(items)}")
        await interaction.response.send_message(embed=items[0], view=Carousel(items))

    @client.tree.command(description="Game")
    async def game(interaction: discord.Interaction):
        doc = users_collection.find_one({"user_id": interaction.user.id})

        # Create both users to play
        user = User(interaction.user.id,
                    interaction.user.name, doc["team"], "red")
        user2 = User(interaction.user.id,
                     interaction.user.name, doc["team"], "blue")

        # Gathers players from both teams
        players = position_players(user, user2)

        # Select who has the ball first
        selected_player = players[0]
        match = Match(user, user)

        score = await set_scoreboard(interaction)
        game = Game(players, selected_player, match, score, img_result, field)
        game.start_game()
        await interaction.channel.send(file=discord.File("image_resultante.png"), view=game)

    @client.tree.command(description="View and edit your team")
    async def embed(interaction: discord.Interaction):
        emoji_name = "bachira_suit_pcmin"
        for emoji in client.emojis:
            if emoji.name == emoji_name:
                player_positions = {str(emoji): (2, 2)}

        grid_str = create_and_display_grid(player_positions)

        await interaction.response.send_message(f"```\n{grid_str}\n```")

    @client.tree.command(description="View and edit your team")
    async def send_emoji(interaction: discord.Interaction):
        emoji_name = "bachira_suit_pcmin"
        custom_message = "Here's your emoji: "

        for emoji in client.emojis:
            if emoji.name == emoji_name:
                await interaction.response.send_message('[' + str(emoji)+']')

    @client.tree.command(description="Redeem daily EgoCoins")
    async def daily(interaction: discord.Interaction):
        if not await verify_if_user_interaction_exists(interaction):
            return
        doc = users_collection.find_one({"user_id": interaction.user.id})
        if doc["daily_used"]:
            await interaction.response.send_message("{}, you have already redeemed your daily *EgoCoins* !".format(interaction.user.mention))
        else:
            users_collection.update_one({"user_id": interaction.user.id}, {
                                        "$set": {"daily_used": True, "ego_coins": doc["ego_coins"]+200}})
            await interaction.response.send_message("{}, you have received **200** *EgoCoins* ! Your balance is now **{}** *EgoCoins*".format(interaction.user.mention, doc["ego_coins"]+200))

    @client.tree.command(description="Shows current banner")
    async def banner(interaction: discord.Interaction):
        doc = cards_collection.find()
        embeds = []

        cards_with_rating = []

        for card in doc:
            cards_with_rating.append((card, card["rating"]))

        cards_with_rating = sorted(
            cards_with_rating, key=lambda x: x[1], reverse=True)

        for card in cards_with_rating:
            embed = discord.Embed()
            embed.title = card[0]["rarity"].capitalize()
            embed.set_image(url=card[0]["card_image"])
            embed.colour = get_color(card[0]["rarity"])
            embeds.append(embed)

        embeds[0].set_footer(
            text=f"{1}/{len(embeds)}")
        await interaction.response.send_message(embed=embeds[0], view=Carousel(embeds))

    @client.tree.command(description="[WARNING : This will delete all your cards/ressources.] You will have 400 EgoCoins on reroll")
    async def reroll(interaction: discord.Interaction):
        if not await verify_if_user_interaction_exists(interaction):
            return
        if (interaction.user.id == int(admin_id)):
            ego_coins_amount = 999999999
        else:
            ego_coins_amount = 500
        users_collection.update_one(
            {"user_id": interaction.user.id}, {"$set": {"ego_coins": ego_coins_amount, "dropped_images": []}})
        await interaction.response.send_message('Reroll complete {} ! **{}** *EgoCoins* have been credited to your balance.'.format(interaction.user.mention, ego_coins_amount))

    @client.tree.command(description="[ADMIN ONLY] Give credits !")
    async def give_credits(interaction: discord.Interaction, amount: int, user: Optional[discord.User] = None):
        if not await verify_if_user_is_admin(interaction):
            return
        if (user != None):  # Give credits to a specific user
            if not await verify_if_user_mentionned_exists(interaction, user):
                return
            doc = users_collection.find_one({"user_id": user.id})
            ego_coins = doc["ego_coins"]
            users_collection.update_one({"user_id": user.id}, {
                                        "$set": {"ego_coins": ego_coins+amount}})
            if (amount > 0):
                await interaction.response.send_message('**{}** *EgoCoins* gifted to {} ! Balance is now **{}** *EgoPoints*.'.format(amount, user.mention, doc['ego_coins']+amount))
            else:
                await interaction.response.send_message('**{}** *EgoCoins* removed from {} ! Balance is now **{}** *EgoPoints*.'.format(amount, user.mention, doc['ego_coins']+amount))

        else:  # Give credits to all users

            for user in users_collection.find():
                user_id = user["user_id"]
                ego_coins = user["ego_coins"]
                users_collection.update_one({"user_id": user_id}, {
                                            "$set": {"ego_coins": ego_coins+amount}})
            await interaction.response.send_message('**{}** *EgoCoins* gifted to all users !'.format(amount))

    @client.tree.command(description="[ADMIN ONLY] Give cards !")
    async def give_card(interaction: discord.Interaction, card_name: str, user: discord.User):
        if not await verify_if_user_mentionned_exists(interaction, user):
            return
        if not await verify_if_user_is_admin(interaction):
            return
        if not await verify_if_card_exists(interaction, card_name):
            return
        users_collection.update_one({"user_id": user.id}, {
                                    "$push": {"dropped_images": card_name}})
        await interaction.response.send_message('**{}** gifted to {} !'.format(card_name.capitalize(), user.mention))
