import discord
from discord.ext import commands
from discord import app_commands


class VoiceChannelCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name = "join", description="讓黑糖拿鐵加入通話")
    @app_commands.describe(channel = "語音頻道名稱（留空預設為使用者當前所在頻道）")
    async def join(self, interaction: discord.Interaction, channel: discord.VoiceChannel = None):
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


    @app_commands.command(name = "leave", description="讓黑糖拿鐵退出通話")
    async def leave(self, interaction: discord.Interaction):
        # Disconnect the bot if it is currently in a voice channel
        voice_client = interaction.guild.voice_client
        if voice_client:
            await voice_client.disconnect()
            await interaction.response.send_message(f"Disconnected from **{voice_client.channel}**.")
        else:
            await interaction.response.send_message("I'm not in a voice channel!")



# This function is required at the bottom of every cog file!
async def setup(bot):
    await bot.add_cog(VoiceChannelCog(bot))