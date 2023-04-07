import os
import discord
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()
discord_bot_key = os.getenv("DISCORD_BOT_KEY")
discord_bot_key_test = os.getenv("DISCORD_BOT_KEY_TEST")
mongo_db_key = os.getenv("MONGO_DB_KEY")

guild_id_dev = os.getenv("GUILD_ID_DEV")
guild_id_test_bot = os.getenv("GUILD_ID_TEST_BOT")
guild_id_blue_lock = os.getenv("GUILD_ID_BLUE_LOCK")
admin_id = os.getenv("ADMIN_ID")
MY_GUILD = discord.Object(id=guild_id_dev)

client_mongo = MongoClient(
    mongo_db_key)
db = client_mongo["BlueLOCK"]
users_collection = db["users"]
cards_collection = db["cards"]

intents = discord.Intents.default()
