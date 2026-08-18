import os
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv

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

@bot.event
async def on_message(message):
    # 1. Ignore messages sent by the bot itself to prevent infinite loops
    if message.author == bot.user:
        return

    # Convert the message to lowercase so it catches "apple", "Apple", and "APPLE"
    msg_text = message.content.lower()

    # --- Trigger 1: Exact match ---
    if msg_text == "hello bot":
        await message.channel.send("Hello there!")

    # --- Trigger 2: Keyword match (anywhere in the sentence) ---
    if "合影" in msg_text:
        heying = [
            "有神快拜 🛐",
            "太強了是電機電神 ⚡️",
            "羨慕合影 🥺"
        ]

        chosen_heying = random.choice(heying)
        
        await message.channel.send(chosen_heying)

    # 2. CRUCIAL: You MUST include this line at the bottom to make the commands work
    await bot.process_commands(message)

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
bot.run(TOKEN)