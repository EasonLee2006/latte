import discord
from discord.ext import commands
from discord import app_commands
from typing import Literal
import database 
import random

class WordCountCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # EVENT: Notice the new decorator
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author == self.bot.user:
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
            database.addCount(user_id, "heying", 1)

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
            database.addCount(user_id, "pofang", 1)
            
            # React to the message to show it counted!
            await message.add_reaction("🏚️")

        # --- six_seven ---
        six_seven = [
            "67",
            "六七",
            ":67:",
            "6️⃣7️⃣",
            "6️⃣ 7️⃣",
        ]
        if any(word in msg_text for word in six_seven):
            database.addCount(user_id, "six_seven", 1)

            six_seven_emoji = discord.utils.get(message.guild.emojis, name='67')
            if six_seven_emoji:
                await message.add_reaction(six_seven_emoji)
            else:
                await message.add_reaction("6️⃣")
                await message.add_reaction("7️⃣")





    @app_commands.command(name = "pofang", description="查看某人破防了幾次")
    @app_commands.describe(target = "搜尋目標（留空預設為自己）")
    async def pofang(self, interaction: discord.Interaction, target: discord.Member = None):
        if target is None:
            target = interaction.user

        user_id = str(target.id)

        result = database.getCount( user_id, "pofang" )
        
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


    @app_commands.command(name = "heying", description="查看某人膜拜了幾次合影")
    @app_commands.describe(target = "搜尋目標（留空預設為自己）")
    async def heying(self, interaction: discord.Interaction, target: discord.Member = None):
        if target is None:
            target = interaction.user

        user_id = str(target.id)

        result = database.getCount( user_id, "heying" )

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



# This function is required at the bottom of every cog file!
async def setup(bot):
    await bot.add_cog(WordCountCog(bot))