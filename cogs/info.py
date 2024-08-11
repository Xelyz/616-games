import discord
from discord.ext import commands

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='arcaea game info')
    async def info(self, ctx, song=None):
        if song == None:
            await ctx.send('''
"A harmony of Light awaits you in a lost world of musical Conflict."

In a world of white, and surrounded by “memory”, two girls awaken under glass-filled skies.

Arcaea is a mobile rhythm game for both experienced and new rhythm game players alike, blending novel gameplay, immersive sound, and a powerful story of wonder and heartache. Experience gameplay that reflects the story's emotions and events—and progress to unlock more of this unfurling narrative.
Challenging trials can be discovered through play, higher difficulties can be unlocked, and a real-time online mode is available to face off against other players.
''')
        else:
            pass

async def setup(bot):
    await bot.add_cog(Info(bot))