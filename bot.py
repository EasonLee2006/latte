import json
import os
import random
import discord
from discord.ext import commands
from discord import app_commands
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

# sync the slash commands
MY_GUILD = discord.Object(id=1112239972842479636)
@bot.event
async def setup_hook():
    # This sends your slash commands to Discord's servers
    bot.tree.copy_global_to(guild=MY_GUILD)
    await bot.tree.sync(guild=MY_GUILD)
    print("Slash commands synced!")


@bot.event
async def on_ready():
    print(f'Success! Logged in as {bot.user}')

@bot.command()
async def hello(ctx):
    # ctx (context) contains info about who sent the message and where
    await ctx.send(f'Hello {ctx.author.name}!')

@bot.tree.command(name = "join", description="讓黑糖拿鐵加入通話")
@app_commands.describe(channel = "語音頻道名稱（留空預設為使用者當前所在頻道）")
async def join(interaction: discord.Interaction, channel: discord.VoiceChannel = None):
    # handle the channel
    if channel is not None:
        pass
    elif interaction.user.voice:
        channel = interaction.user.voice.channel
    else:
        await interaction.response.send_message("You need to join a voice channel first, or specify the channel.")
        return


    # 3. Connect to the channel (or get the existing connection)
    voice_client = interaction.guild.voice_client

    if voice_client is None:
        await channel.connect()
        await interaction.response.send_message(f"Joined **{channel.name}**!")
    else:
        await voice_client.move_to(channel)
        await interaction.response.send_message(f"Moved to **{channel.name}**!")

@bot.tree.command(name = "leave", description="讓黑糖拿鐵退出通話")
async def leave(interaction: discord.Interaction):
    # Disconnect the bot if it is currently in a voice channel
    voice_client = interaction.guild.voice_client
    if voice_client:
        await voice_client.disconnect()
        await interaction.response.send_message(f"Disconnected from **{voice_client.channel}**.")
    else:
        await interaction.response.send_message("I'm not in a voice channel!")

# helper function for adding counts
def addCount(stats, user_id, category, ammount):
    if(user_id not in stats):
        stats[user_id] = {}

    if( category not in stats[user_id] ):
        stats[user_id][category] = 0

    stats[user_id][category] += ammount
    return stats

@bot.tree.command(name = "pofang", description="查看某人破防了幾次")
@app_commands.describe(target = "搜尋目標（留空預設為自己）")
async def pofang(interaction: discord.Interaction, target: discord.Member = None):
    if target is None:
        target = interaction.user

    stats = load_stats()
    user_id = str(target.id)
    
    # Check if they are in the database
    if ( user_id in stats ) and ( "pofang_count" in stats[user_id] ):
        count = stats[user_id]["pofang_count"]
        if (target == interaction.user):
            await interaction.response.send_message(f"你總共破防了{count}次，豪可憐喔～")
        else:
            await interaction.response.send_message(f"**{target.name}**總共破防了{count}次，該怎麼讓他破防更多次呢？")
    else:
        if (target == interaction.user):
            await interaction.response.send_message(f"你還沒在我眼前破防過，要不要破防一下？")
        else:
            await interaction.response.send_message(f"**{target.name}**還沒破防過，他的心態十分良好")
        

@bot.tree.command(name = "heying", description="查看某人膜拜了幾次合影")
@app_commands.describe(target = "搜尋目標（留空預設為自己）")
async def heying(interaction: discord.Interaction, target: discord.Member = None):
    if target is None:
        target = interaction.user

    stats = load_stats()
    user_id = str(target.id)
    
    # Check if they are in the database
    if ( user_id in stats ) and ( "heying_count" in stats[user_id] ):
        count = stats[user_id]["heying_count"]
        if (target == interaction.user):
            await interaction.response.send_message(f"你膜拜了{count}次何電神，必有福報")
        else: 
            await interaction.response.send_message(f"**{target.name}**膜拜了{count}次何電神，是個忠實的信徒")
    else:
        if (target == interaction.user):
            await interaction.response.send_message(f"你還沒膜拜過我們的唯一真神，還不快點膜拜 😡")
        else:
            await interaction.response.send_message(f"**{target.name}**還沒提及我們的唯一真神，必會遭到天譴")


@bot.event
async def on_message(message):
    # 1. Ignore messages sent by the bot itself to prevent infinite loops
    if message.author == bot.user:
        return

    msg_text = message.content.lower()

    # --- Exact match ---
    if msg_text == "hello bot":
        await message.channel.send("Hello there!")

    # --- heying ---
    heying = [
        "合影",
        "何影",
        "合穎",
        "何穎",
    ]
    if any(word in msg_text for word in heying):

        heying_reply = [
            "有神快拜 🛐",
            "太強了是電機電神 ⚡️",
            "羨慕合影 🥺"
        ]

        chosen_heying_reply = random.choice(heying_reply)
        await message.channel.send(chosen_heying_reply)

        # save heying count
        stats = load_stats()
        user_id = str(message.author.id)
        new_stats = addCount(stats, user_id, "heying_count", 1)
        save_stats(new_stats)

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
        
        new_stats = addCount(stats, user_id, "pofang_count", 1)
        
        save_stats(new_stats)
        
        # React to the message to show it counted!
        await message.add_reaction("🏚️")


    # MUST include this line at the bottom to make the commands work
    await bot.process_commands(message)

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
bot.run(TOKEN)