import discord
from discord.ext import commands
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()
PWD = os.getenv('PASSWORD')
# Establish connection
conn = mysql.connector.connect(user='discordbot', password=PWD, host='localhost', database='arcaeaSongInfo')
cursor = conn.cursor()

def ToLowerCase(arg):
    return arg.lower()

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    @commands.command()
    async def play(self, ctx, game_name: ToLowerCase):
        channel_id = ctx.channel.id
        if channel_id not in self.games:
            match game_name:
                case 'hangman':
                    # self.games[channel_id] = game = Hangman()
                    await Hangman().startGameMsg(ctx)
                case _:
                    await ctx.send('Game Not Found.')
        else:
            await ctx.send("A game is already running in this channel!")

    @commands.command()
    async def endgame(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in self.games:
            await ctx.send(f'{self.games[channel_id].name} in this channel ended...')
            del self.games[channel_id]
        else:
            await ctx.send('There are no games running in this channel...')

    @commands.command()
    async def rand(self, ctx):
        cursor.execute('SELECT * FROM songs ORDER BY RAND() LIMIT 1')
        await ctx.send(cursor.fetchone())

class Hangman():
    def __init__(self):
        self.name = 'hangman'

    async def startGameMsg(self, ctx):
        await ctx.send('game still under development')

async def setup(bot):
    await bot.add_cog(Play(bot))