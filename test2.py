import discord
from discord.ext import commands

from dotenv import load_dotenv
import os
load_dotenv()
intents = discord.Intents.default()
intents.message_content = True

discord_bot_key = os.getenv("DISCORD_BOT_KEY")

# Define the bot client
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


# Define a command


@bot.command()
async def hello(ctx):
    print("hello() function called")
    await ctx.send("Hello!")

# Run the bot
bot.run(discord_bot_key)
