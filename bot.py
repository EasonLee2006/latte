import json
import os
import random
import time
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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS voice_stats (
            user_id TEXT,
            channel_id TEXT,
            total_seconds INTEGER DEFAULT 0,
            PRIMARY KEY (user_id, channel_id)
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


def second_to_time_string( second ):
    # Convert raw seconds into hours, minutes, and seconds
    hours, remainder = divmod(second, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    # Build a nice time string (e.g., "2h 15m 30s")
    time_str = ""
    if hours > 0: time_str += f"{hours}小時"
    if minutes > 0 or hours > 0: time_str += f"{minutes}分"
    time_str += f"{seconds}秒"

    return time_str.strip()

# Dropdown menu for "Voice" leaderboard
class VoiceChannelSelect(discord.ui.ChannelSelect):
    def __init__(self):
        super().__init__(
            placeholder="選擇語音頻道...",
            min_values=1,
            max_values=1,
            channel_types=[discord.ChannelType.voice] 
        )

    async def callback(self, interaction: discord.Interaction):
        selected_channel = self.values[0]
        channel_id = str(selected_channel.id)
        
        conn = sqlite3.connect("stats.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT user_id, total_seconds 
            FROM voice_stats 
            WHERE channel_id = ? AND total_seconds > 0 
            ORDER BY total_seconds DESC 
            LIMIT 5
        """, (channel_id,))
        top_users = cursor.fetchall()
        conn.close()

        embed = discord.Embed(
            title=f"🏆 Voice Time Leaderboard: <#{channel_id}> 🏆",
            color=discord.Color.blue()
        )
        
        if not top_users:
            embed.description = "還沒有人上榜..."
        else:
            board_text = ""
            for index, row in enumerate(top_users, start=1):
                user_id = row[0]
                score = row[1]

                emoji = "⏱️"
                
                board_text += f"`{index}.` <@{user_id}>\n     {emoji} **{second_to_time_string(score)}**\n"

            embed.description = board_text
            
        embed.set_footer(text=f"Filtered by {interaction.user.display_name}")
        await interaction.response.edit_message(embed=embed, view=self.view)


class VoiceLeaderboardView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(VoiceChannelSelect())

    # --- NEW: Add the Global Button ---
    # The @discord.ui.button decorator automatically adds this to the View
    @discord.ui.button(label="🌐 Global Total", style=discord.ButtonStyle.primary)
    async def global_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        conn = sqlite3.connect("stats.db")
        cursor = conn.cursor()
        
        # We run the exact same SUM() query from the main command
        cursor.execute("""
            SELECT user_id, total_seconds, channel_id
            FROM voice_stats
            ORDER BY total_seconds DESC 
            LIMIT 5
        """)
        top_users = cursor.fetchall()
        conn.close()

        embed = discord.Embed(
            title="🏆 Voice Time Leaderboard 🏆",
            color=discord.Color.blue()
        )
        
        if not top_users:
            embed.description = "還沒有人在榜上..."
        else:
            board_text = ""
            for index, row in enumerate(top_users, start=1):
                user_id = row[0]
                score = row[1]
                channel_id = row[2]

                emoji = "⏱️"
                
                board_text += f"`{index}.` <@{user_id}> at <#{channel_id}> \n     {emoji} **{second_to_time_string(score)}**\n"

            embed.description = board_text

        embed.set_footer(text=f"Global view restored by {interaction.user.display_name}")
        
        # Edit the message back to the Global view
        await interaction.response.edit_message(embed=embed, view=self)


# --- leaderboard ---
@bot.tree.command(name="leaderboard", description="查看對應項目的前五名")
# The Literal creates the dropdown menu in Discord!
async def leaderboard(interaction: discord.Interaction, category: Literal["pofang", "heying", "voice"]):
    conn = sqlite3.connect("stats.db")
    cursor = conn.cursor()

    if category == "voice":
        cursor.execute("""
            SELECT user_id, total_seconds, channel_id
            FROM voice_stats
            ORDER BY total_seconds DESC 
            LIMIT 5
        """)
        top_users = cursor.fetchall()
        emoji = "⏱️"
        embed_color = discord.Color.blue()
        title_name = "Voice Time"

    else:
        column = f"{category}_count"

        # Ask SQLite to fetch the top 5 users directly! No Python sorting needed.
        cursor.execute(f"SELECT user_id, {column} FROM users WHERE {column} > 0 ORDER BY {column} DESC LIMIT 5")
        top_users = cursor.fetchall()
        emoji = "🏚️" if category == "pofang" else "🛐"
        title_name= category.capitalize()
        embed_color = discord.Color.orange() if category == "pofang" else discord.Color.purple()

    conn.close()

    
    # Pick the right emoji for the message
    
    embed = discord.Embed(
        title=f"🏆 {title_name} Leaderboard 🏆",
        color=embed_color
    )

    if not top_users:
        board_text = "還沒有人在榜上..."
        embed.description = board_text
        await interaction.response.send_message(
            embed=embed, 
            allowed_mentions=discord.AllowedMentions.none()
        )
        return

    board_text = ""
    for index, row in enumerate(top_users, start=1):
        user_id = row[0]
        score = row[1]

        if category == "voice":
            channel_id = row[2]

            board_text += f"`{index}.` <@{user_id}> at <#{channel_id}> \n     {emoji} **{second_to_time_string(score)}**\n"
        else:
            board_text += f"`{index}.` <@{user_id}> \n     {emoji} **{score}**\n"


    embed.description = board_text

    embed.set_footer(text=f"Requested by {interaction.user.display_name}")

    if category == "voice":
        await interaction.response.send_message(
            embed=embed, 
            view=VoiceLeaderboardView(),
            allowed_mentions=discord.AllowedMentions.none()
        )
    else:
        await interaction.response.send_message(
            embed=embed, 
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

import time

# This dictionary acts as our live stopwatch for everyone in the server
voice_sessions = {}

@bot.event
async def on_voice_state_update(member, before, after):
    # If the user changed channels (or joined/left)
    if before.channel != after.channel:
        
        # 1. Did they LEAVE a channel? (Stop the stopwatch)
        if before.channel is not None:
            # Get their session data and remove it from the dictionary
            session = voice_sessions.pop(member.id, None)
            
            if session and session['channel_id'] == before.channel.id:
                # Calculate how many seconds they were in there
                elapsed_seconds = int(time.time() - session['start_time'])
                
                # Save it to the database
                conn = sqlite3.connect("stats.db")
                cursor = conn.cursor()
                
                # Make sure the row exists first
                cursor.execute(
                    "INSERT OR IGNORE INTO voice_stats (user_id, channel_id) VALUES (?, ?)", 
                    (str(member.id), str(before.channel.id))
                )
                
                # Add the new seconds to their total
                cursor.execute(
                    "UPDATE voice_stats SET total_seconds = max(total_seconds, ?) WHERE user_id = ? AND channel_id = ?", 
                    (elapsed_seconds, str(member.id), str(before.channel.id))
                )
                
                conn.commit()
                conn.close()

        # 2. Did they JOIN a channel? (Start the stopwatch)
        if after.channel is not None:
            voice_sessions[member.id] = {
                "channel_id": after.channel.id,
                "start_time": time.time()
            }

@bot.event
async def on_message(message):
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