import discord
from discord.ext import commands

from ..hangman import Hangman

def ToLowerCase(arg):
    return arg.lower()

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, game: ToLowerCase):
        match game:
            case 'hangman':
                #implement logic when complete the game
                game = Hangman()
                ctx.send(game.startGameMsg())
            case _:
                ctx.send('Game Not Found.')


async def setup(bot):
    await bot.add_cog(Play(bot))