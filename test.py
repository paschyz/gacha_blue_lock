# db.users.update_one({"user_id": user_ids}, {"command_used": True})
import discord
import os
import random
from dotenv import load_dotenv
import pymongo
from pymongo import MongoClient
from discord import Interaction, app_commands, ui
from discord.ext import commands, tasks
from discord.utils import MISSING

load_dotenv()

discord_bot_key = os.getenv("DISCORD_BOT_KEY")

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(command_prefix='/', intents=intents)


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.command()
async def hello(ctx):
    await ctx.send('Hello, world!')


client.run(
    discord_bot_key)
