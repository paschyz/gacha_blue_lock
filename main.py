from client import MyClient
from config import discord_bot_key, discord_bot_key_test, intents
from commands import setup_commands

client = MyClient(intents=intents)
setup_commands(client)
client.run(discord_bot_key)
