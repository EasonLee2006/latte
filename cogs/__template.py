import discord
from discord.ext import commands
from discord import app_commands
import database 


class CogNameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # EVENT: Notice the new decorator
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return


    @app_commands.command(name = "pofang", description="查看某人破防了幾次")
    @app_commands.describe(target = "搜尋目標（留空預設為自己）")
    async def pofang(self, interaction: discord.Interaction, target: discord.Member = None):
        if target is None:
            target = interaction.user
        



# This function is required at the bottom of every cog file!
async def setup(bot):
    await bot.add_cog(CogNameCog(bot))