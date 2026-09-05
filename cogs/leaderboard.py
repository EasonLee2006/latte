import discord
import sqlite3
from discord.ext import commands
from discord import app_commands
import database 
from typing import Literal

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



class LeaderboardCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name="leaderboard", description="查看對應項目的前五名")
    # The Literal creates the dropdown menu in Discord!
    async def leaderboard(self, interaction: discord.Interaction, category: Literal["pofang", "heying", "six_seven", "voice"]):
    
        result = database.getTopUsers(category = category, number = 5)
        
        top_users = result["top_users"]
        emoji = result["emoji"]
        embed_color = result["embed_color"]
        title_name = result["title_name"]
        
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
 



# This function is required at the bottom of every cog file!
async def setup(bot):
    await bot.add_cog(LeaderboardCog(bot))