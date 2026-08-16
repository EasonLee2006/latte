import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

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


# Replace 'YOUR_TOKEN_HERE' with the token you copied from the Developer Portal

bot.run(TOKEN)