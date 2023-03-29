from config import guild_id_dev, guild_id_test_bot, guild_id_blue, mongo_db_key
from utils import *
from carousel import Carousel
from client import MyClient
from pymongo import MongoClient
from typing import Optional

client_mongo = MongoClient(mongo_db_key)
db = client_mongo["BlueLOCK"]
users_collection = db["users"]
cards_collection = db["cards"]

def setup_commands(client: MyClient):
    @client.event
    async def on_ready():
        print('Logged in as {0.user}!'.format(client))


    @client.tree.command(description="Give credits ! Only for admins !")
    async def give_credits(interaction: discord.Interaction, amount: int, user: Optional[discord.User] = None):
        required_role = discord.utils.get(interaction.guild.roles, name='Admin')
        if required_role in interaction.user.roles:
            if (user != None):

                user_id = user.id
                doc = users_collection.find_one({"user_id": user_id})
                if doc is None:
                    await interaction.response.send_message('{}, this user is not registered !'.format(interaction.user.mention))
                else:
                    ego_coins = doc["ego_coins"]
                    users_collection.update_one({"user_id": user_id}, {
                                                "$set": {"ego_coins": ego_coins+amount}})
                    await interaction.response.send_message('{} credits given to {} !'.format(amount, interaction.user.mention))

            else:

                for user in users_collection.find():
                    user_id = user["user_id"]
                    ego_coins = user["ego_coins"]
                    users_collection.update_one({"user_id": user_id}, {
                                                "$set": {"ego_coins": ego_coins+amount}})
                await interaction.response.send_message('{} credits given to all users !'.format(amount))
        else:
            await interaction.response.send_message('You are not an admin ! You are not authorized to use this command !')


    @client.tree.command(description="Conquer this world with your ego !")
    async def register(interaction: discord.Interaction):
        doc = users_collection.find_one({"user_id": interaction.user.id})
        if doc is None:
            user_id = interaction.user.id
            user = str(interaction.user)
            users_collection.insert_one(
                {"user_id": user_id, "username": user, "ego_coins": 400, "dropped_images": []})
            await interaction.response.send_message('Register complete {} ! Have fun :)'.format(interaction.user.mention))
        else:
            await interaction.response.send_message('{}, you are already registered !'.format(interaction.user.mention))


    @client.tree.command(description="Shows your EgoCoins !")
    async def balance(interaction: discord.Interaction):
        doc = users_collection.find_one({"user_id": interaction.user.id})
        if doc is None:
            await interaction.response.send_message('User not registered ! Use /register command')
        else:
            await interaction.response.send_message('{}, you have **{}** *EgoCoins* !'.format(interaction.user.mention, doc['ego_coins']))


    @client.tree.command(description="Shows your inventory !")
    async def inventory(interaction: discord.Integration):
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
                                        color=color,
                                        )
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


    @client.tree.command(description="Reroll your account !    WARNING : This will delete your inventory and all you ressources !")
    async def reroll(interaction: discord.Interaction):
        if (verify_if_user_exists(interaction.user.id)):
            users_collection.update_one(
                {"user_id": interaction.user.id}, {"$set": {"ego_coins": 400, "dropped_images": []}})
            await interaction.response.send_message('Reroll complete !')
        else:
            await interaction.response.send_message('User not registered ! Use /register command')


    @client.tree.command(description="Summon players ! **100 EgoCoins per summon** |  Common (54.5%) Rare (40%) Epic (5%) Legendary (0.5%)")
    async def summon(interaction: discord.Interaction, number_of_summons: int):
        if (verify_if_user_exists(interaction.user.id)):
            doc = users_collection.find_one({"user_id": interaction.user.id})
            ego_coins = doc["ego_coins"]
            items = []

            if (ego_coins >= number_of_summons*100):
                users_collection.update_one({"user_id": interaction.user.id}, {
                                            "$set": {"ego_coins": ego_coins - number_of_summons*100}})
                for i in range(number_of_summons):
                    getcard = await roll_summon_category(get_card_rarity())
                    embed = discord.Embed(colour=discord.Colour.red())
                    embed.set_image(url=getcard["card_image"])
                    embed.title = "{}'s summon n°{}".format(
                        interaction.user.name, i+1)
                    embed.set_footer(text="{}/{}".format(i+1, number_of_summons))
                    embed.colour = getcard["color"]
                    users_collection.update_one(
                        {"user_id": interaction.user.id},
                        {"$push": {"dropped_images": getcard["name"].lower()}}
                    )
                    items.append(embed)

                await interaction.response.send_message(embed=items[0], view=Carousel(items))

                await interaction.channel.send("{}, {} *EgoCoins used*. You have now **{}** *EgoCoins left* !".format(interaction.user.mention, number_of_summons*100, doc['ego_coins']-number_of_summons*100))
            else:
                await interaction.response.send_message('Not enough credits. You have **{}** *EgoCoins* !'.format(doc['ego_coins']))
        else:
            await interaction.response.send_message('User not registered ! Use /register command')


    @client.tree.command(description="Show current banner !")
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