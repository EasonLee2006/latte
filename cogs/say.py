import discord
from discord.ext import commands
from discord import app_commands


class SayCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # EVENT: Notice the new decorator
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return


    @app_commands.command(name = "say", description="repeat after you")
    @app_commands.describe(content = "things you want latte to say")
    async def pofang(self, interaction: discord.Interaction, content: str):
        if content is not None:
            await interaction.response.send_message(content)
            return
        else:
            await interaction.response.send_message("please enter content")
            return
        



# This function is required at the bottom of every cog file!
async def setup(bot):
    await bot.add_cog(SayCog(bot))