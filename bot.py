import json
import os
import random
import discord
import sqlite3
from typing import Literal
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# === stats ===
def init_db():
    # This creates 'stats.db' in your folder if it doesn't exist
    conn = sqlite3.connect("stats.db")
    cursor = conn.cursor()
    
    # Create a table with 3 columns. 
    # 'PRIMARY KEY' means every user_id is unique; no duplicates allowed!
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            pofang_count INTEGER DEFAULT 0,
            heying_count INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

def migrate_json_to_db():
    # 1. Check if the old JSON file still exists
    JSON_DATA = "data/stats.json"
    if not os.path.exists(JSON_DATA):
        return 

    print(f"Found {JSON_DATA}! Starting migration to SQLite...")
    
    # 2. Open and read the old JSON data
    with open(JSON_DATA, "r") as f:
        stats = json.load(f)

    conn = sqlite3.connect("stats.db")
    cursor = conn.cursor()

    # 3. Loop through every user in the JSON file
    for user_id, data in stats.items():
        heyings = data.get("heying_count", 0)
        pofangs = data.get("pofang_count", 0)
        
        # INSERT OR REPLACE ensures that if the user is already in the database 
        # for some reason, their stats get safely overwritten with the JSON stats
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, heying_count, pofang_count) 
            VALUES (?, ?, ?)
        ''', (user_id, heyings, pofangs))

    conn.commit()
    conn.close()

    # 4. Rename the JSON file so the bot never tries to migrate it again
    os.rename(JSON_DATA, "data/stats_backup.json")
    print("Migration complete! stats.json was renamed to stats_backup.json")


init_db()
migrate_json_to_db() 


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
    await bot.tree.sync()
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


@bot.tree.command(name = "pofang", description="查看某人破防了幾次")
@app_commands.describe(target = "搜尋目標（留空預設為自己）")
async def pofang(interaction: discord.Interaction, target: discord.Member = None):
    if target is None:
        target = interaction.user

    user_id = str(target.id)

    conn = sqlite3.connect("stats.db")
    cursor = conn.cursor()
    # Fetch just the apple_count for this specific user
    cursor.execute("SELECT pofang_count FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    
    # Check if they are in the database
    if result and result[0]>0:
        if (target == interaction.user):
            await interaction.response.send_message(f"你總共破防了{result[0]}次，豪可憐喔～")
        else:
            await interaction.response.send_message(f"**{target.name}**總共破防了{result[0]}次，該怎麼讓他破防更多次呢？")
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

    user_id = str(target.id)

    conn = sqlite3.connect("stats.db")
    cursor = conn.cursor()
    # Fetch just the apple_count for this specific user
    cursor.execute("SELECT heying_count FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()

    # easter egg
    HEYING_ID = 910383175258222632
    if (target.id == HEYING_ID and interaction.user.id == HEYING_ID): # 合影
                await interaction.response.send_message(f"你是電，你是光，你是唯一的神話 ⚡")
                return
    if (target.id == HEYING_ID and interaction.user.id != HEYING_ID):
        await interaction.response.send_message(f"他是我們的唯一真神。請說：謝謝合影")
        return
    
    # Check if they are in the database
    if result and result[0] > 0:
        if (target == interaction.user):
            await interaction.response.send_message(f"你膜拜了{result[0]}次何電神，必有福報")
            return
        else: 
            await interaction.response.send_message(f"**{target.name}**膜拜了{result[0]}次何電神，是個忠實的信徒")
            return
    else:        
        if (target == interaction.user):
            await interaction.response.send_message(f"你還沒膜拜過我們的唯一真神，還不快點膜拜 😡")
            return
        else:
            await interaction.response.send_message(f"**{target.name}**還沒提及我們的唯一真神，必會遭到天譴")
            return


@bot.tree.command(name="leaderboard", description="查看對應項目的前五名")
# The Literal creates the dropdown menu in Discord!
async def leaderboard(interaction: discord.Interaction, category: Literal["pofang", "heying"]):
    column = f"{category}_count"
    
    conn = sqlite3.connect("stats.db")
    cursor = conn.cursor()
    # Ask SQLite to fetch the top 5 users directly! No Python sorting needed.
    cursor.execute(f"SELECT user_id, {column} FROM users WHERE {column} > 0 ORDER BY {column} DESC LIMIT 5")
    top_users = cursor.fetchall()
    conn.close()
    
    if not top_users:
        await interaction.response.send_message("Database is empty...")
        return
    
    # Pick the right emoji for the message
    emoji = "🏚️" if category == "pofang" else "🛐"
    
    message_text = f"🏆 **{category.capitalize()} Leaderboard** 🏆\n\n"
    
    for index, row in enumerate(top_users, start=1):
        user_id = row[0]
        count = row[1]
        message_text += f"**{index}.** <@{user_id}> —— {count} {emoji}\n"
        
    await interaction.response.send_message(
        message_text, 
        allowed_mentions=discord.AllowedMentions.none()
    )


# helper function for adding counts
def addCount(user_id: str, category: str, amount: int = 1):
    # 1. SECURITY: Whitelist allowed categories to prevent SQL Injection
    allowed_categories = ["pofang", "heying"] # Add future categories here!
    
    if category not in allowed_categories:
        print(f"Error: Category '{category}' is not allowed in the database.")
        return
        
    column_name = f"{category}_count"
    
    conn = sqlite3.connect("stats.db")
    cursor = conn.cursor()
    
    # 2. Make sure the user exists first
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
    
    # 3. Safely inject the column name with an f-string, but use ? for the values
    query = f"UPDATE users SET {column_name} = {column_name} + ? WHERE user_id = ?"
    cursor.execute(query, (amount, user_id))
    
    conn.commit()
    conn.close()

@bot.event
async def on_message(message):
    # 1. Ignore messages sent by the bot itself to prevent infinite loops
    if message.author == bot.user:
        return

    msg_text = message.content.lower()

    # --- Exact match ---
    if msg_text == "hello bot":
        await message.channel.send("Hello there!")
        return

    user_id = str(message.author.id)

    # --- heying ---
    heying = [
        "合影",
        "何影",
        "合穎",
        "何穎",
    ]
    if any(word in msg_text for word in heying):

        # save heying count
        addCount(user_id, "heying", 1)

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
        ":house_abandoned:",
        "pdf"
    ]
    if any(word in msg_text for word in pofang):
        addCount(user_id, "pofang", 1)
        
        # React to the message to show it counted!
        await message.add_reaction("🏚️")

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')
bot.run(TOKEN)