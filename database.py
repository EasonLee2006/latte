import json
import os
import sqlite3
import discord


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
            six_seven_count INTEGER DEFAULT 0
        )
    ''')


    # Add column six_seven_count if it is missing
    cursor.execute("PRAGMA table_info(users)")
    columns = [info[1] for info in cursor.fetchall()]

    if "six_seven_count" not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN six_seven_count INTEGER DEFAULT 0")
        print("Added collumn six_seven_count.")


    # table for voice stats
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


# Whitelist allowed categories to prevent SQL Injection
# [[[ IMPORTANT ]]] remember to also change init_db 
allowed_categories = ["pofang", "heying", "six_seven", "voice"] # Add future categories here!

# to check if the category passed in is safe
def safety_check(category):
    if category in allowed_categories:
        return True

    print(f"Error: Category '{category}' is not allowed in the database.")
    return False

def getCount(user_id: str, category: str):
    if not safety_check(category):
        return

    column_name = f"{category}_count"

    conn = sqlite3.connect("stats.db")
    cursor = conn.cursor()

    # Fetch just the apple_count for this specific user

    query = f"SELECT {column_name} FROM users WHERE user_id = ?"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()
    conn.close()

    return result

# helper function for adding counts
def addCount(user_id: str, category: str, amount: int = 1):
    
    if not safety_check(category):
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


# helper function for updaing voice stats
def update_voice_stats( member_id: str, before_channel_id: str, elapsed_seconds ):
    # Save it to the database
    conn = sqlite3.connect("stats.db")
    cursor = conn.cursor()

    # Make sure the row exists first
    cursor.execute(
        "INSERT OR IGNORE INTO voice_stats (user_id, channel_id) VALUES (?, ?)", 
        (member_id, before_channel_id)
    )

    # Add the new seconds to their total
    cursor.execute(
        "UPDATE voice_stats SET total_seconds = max(total_seconds, ?) WHERE user_id = ? AND channel_id = ?", 
        (elapsed_seconds, member_id, before_channel_id)
    )

    conn.commit()
    conn.close()


def getTopUsers( category: str, number ):
    if not safety_check(category):
        return

    conn = sqlite3.connect("stats.db")
    cursor = conn.cursor()

    result = {}

    if category == "voice":
        query = f"""
            SELECT user_id, total_seconds, channel_id
            FROM voice_stats
            ORDER BY total_seconds DESC 
            LIMIT {number}
        """
        cursor.execute(query)

        result["top_users"] = cursor.fetchall()

        result["emoji"] = "⏱️"
        result["embed_color"] = discord.Color.blue()
        result["title_name"] = "Voice Time"

    if category == "six_seven":
        column = f"{category}_count"

        query = f"SELECT user_id, {column} FROM users WHERE {column} > 0 ORDER BY {column} DESC LIMIT {number}"
        cursor.execute(query)

        result["top_users"] = cursor.fetchall()
        result["emoji"] = "6️⃣7️⃣"
        result["embed_color"] = discord.Color.yellow()
        result["title_name"] = "6️⃣7️⃣"

    else:
        column = f"{category}_count"

        query = f"SELECT user_id, {column} FROM users WHERE {column} > 0 ORDER BY {column} DESC LIMIT {number}"
        cursor.execute(query)

        result["top_users"] = cursor.fetchall()
        result["emoji"] = "🏚️" if category == "pofang" else "🛐"
        result["embed_color"] = discord.Color.orange() if category == "pofang" else discord.Color.purple()
        result["title_name"] = category.capitalize()

    conn.close()

    return result