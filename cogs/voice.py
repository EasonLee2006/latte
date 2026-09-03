import time
from discord.ext import commands
import database

class VoiceCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Move your in-memory stopwatch dictionary here so it's attached to the Cog
        self.voice_sessions = {}

    # EVENT: Notice the 'self' parameter added to the function
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            # Did they leave?
            if before.channel is not None:
                # Use self.voice_sessions
                session = self.voice_sessions.pop(member.id, None)
                
                if session and session['channel_id'] == before.channel.id:
                    elapsed_seconds = int(time.time() - session['start_time'])
                    
                    database.update_voice_stats( str(member.id), str(before.channel.id), elapsed_seconds )

            # Did they join?
            if after.channel is not None:
                self.voice_sessions[member.id] = {
                    "channel_id": after.channel.id,
                    "start_time": time.time()
                }


async def setup(bot):
    await bot.add_cog(VoiceCog(bot))