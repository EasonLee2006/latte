import json
import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv

# === stats ===
STATS_FILE = "./data/stats.json"

def load_stats():
    # If the file exists, open it and read the data
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    # If it's the bot's first time running, the file won't exist, so return an empty dictionary
    except FileNotFoundError:
        return {}

def save_stats(data):
    # Write the updated data back into the file
    with open(STATS_FILE, "w") as f:
        # indent=4 makes the file nicely formatted so you can easily read it yourself
        json.dump(data, f, indent=4)


# === commands ===
# Intents dictate what events your bot is allowed to listen to
intents = discord.Intents.default()
intents.message_content = True  

# '!' will be the prefix for your bot's commands (e.g., !hello)
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Success! Logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    # ctx (context) contains info about who sent the message and where
    await ctx.send(f'Hello {ctx.author.name}!')

@bot.command()
async def join(ctx):
    # 1. Check if the user sending the command is actually in a voice channel
    if not ctx.author.voice:
        await ctx.send("You need to join a voice channel first!")
        return

    # 2. Get the channel the user is in
    user_channel = ctx.author.voice.channel

    # 3. Connect to the channel (or get the existing connection)
    voice_client = ctx.voice_client

    if voice_client is None:
        # The bot is not in any voice channel yet, so it connects fresh
        await user_channel.connect()
        await ctx.send(f"Joined **{user_channel.name}**!")
    else:
        # The bot is already in a channel, so we move it to the user's channel
        await voice_client.move_to(user_channel)
        await ctx.send(f"Moved to **{user_channel.name}**!")

@bot.command()
async def leave(ctx):
    # Disconnect the bot if it is currently in a voice channel
    voice_client = ctx.voice_client
    if voice_client:
        await voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")
    else:
        await ctx.send("I'm not in a voice channel!")

@bot.command()
async def pofang(ctx):
    stats = load_stats()
    user_id = str(ctx.author.id)
    
    # Check if they are in the database
    if user_id in stats:
        count = stats[user_id]["pofang_count"]
        await ctx.send(f"{ctx.author.name}，你總共破防了{count}次，豪可憐喔～")
    else:
        await ctx.send(f"你還沒在我眼前破防過，要不要破防一下？")

@bot.event
async def on_message(message):
    # 1. Ignore messages sent by the bot itself to prevent infinite loops
    if message.author == bot.user:
        return

    msg_text = message.content.lower()

    # return if the message is a command
    if msg_text[0] == bot.get_prefix:
        await bot.process_commands(message)
        return

    # --- Exact match ---
    if msg_text == "hello bot":
        await message.channel.send("Hello there!")

    # --- heying ---
    heying = [
        "合影",
        "何影",
        "合穎",
        "何穎",
        "heying",
        "he ying"
    ]
    if any(word in msg_text for word in heying):
        heying_reply = [
            "有神快拜 🛐",
            "太強了是電機電神 ⚡️",
            "羨慕合影 🥺"
        ]

        chosen_heying_reply = random.choice(heying_reply)
        await message.channel.send(chosen_heying_reply)

    # --- pofang ---
    pofang = [
        "破防",
        "破房",
        "破大防",
        "🏚️",
        ":house_abandoned:"
    ]
    if any(word in msg_text for word in pofang):
        # 1. Load the current stats
        stats = load_stats()
        
        user_id = str(message.author.id)
        
        if user_id not in stats:
            stats[user_id] = {"pofang_count": 0}
        stats[user_id]["pofang_count"] += 1
        
        save_stats(stats)
        
        # React to the message to show it counted!
        await message.add_reaction("🏚️")


    # MUST include this line at the bottom to make the commands work
    await bot.process_commands(message)

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
bot.run(TOKEN)