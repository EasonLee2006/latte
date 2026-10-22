import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import database  # Import your new database file

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
MY_GUILD = discord.Object(id=1112239972842479636)

intents = discord.Intents.default()
intents.message_content = True  
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def setup_hook():
    # 1. Initialize the database
    database.init_db()

    # 2. Load the Cogs
    await bot.load_extension("cogs.word_count")
    await bot.load_extension("cogs.leaderboard")
    await bot.load_extension("cogs.voice")
    await bot.load_extension("cogs.voice_channel")
    await bot.load_extension("cogs.say")
    # await bot.load_extension("cogs.FILENAME") # Uncomment when you make voice.py

    # 3. Sync slash commands
    await bot.tree.sync()
    print("Bot is ready and Cogs are loaded!")

@bot.event
async def on_ready():
    print(f'Success! Logged in as {bot.user}')

bot.run(TOKEN)