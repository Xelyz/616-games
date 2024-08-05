import discord
from discord.ext import commands

class Read(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def read(self, ctx, *, arg):
        await ctx.send(arg)

async def setup(bot):
    await bot.add_cog(Read(bot))