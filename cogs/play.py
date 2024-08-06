import discord
from discord.ext import commands
import os
import mysql.connector
import re
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

    @commands.command(help='Play a mini game!')
    async def play(self, ctx, game_name: ToLowerCase):
        channel_id = ctx.channel.id
        if channel_id not in self.games:
            match game_name:
                case 'hangman':
                    self.games[channel_id] = game = Hangman()
                    await game.startGame(ctx)
                case _:
                    await ctx.send('Game Not Found.\nAvailable Games: Hangman')
        else:
            await ctx.send("A game is already running in this channel!")

    @commands.command(help='Ends the game in the channel')
    async def endgame(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in self.games:
            await ctx.send(f'{self.games[channel_id].name} in this channel ended...')
            del self.games[channel_id]
        else:
            await ctx.send('There are no games running in this channel...')

    @commands.command(help='Hangman game command. View a character')
    async def view(self, ctx, s):
        channel_id = ctx.channel.id
        if channel_id in self.games:
            game = self.games[channel_id]
            msg = game.view(s, ctx.author)
            await game.currState(ctx, msg)
        else:
            await ctx.send('There are no games running. Perhaps you want to start a game by sending \"lowiro-play (game)?\"')

class Hangman():
    def __init__(self):
        self.name = 'hangman'
        self.answer = []
        self.state = []
        self.songs = []
        self.viewed = []

    async def startGame(self, ctx):
        n = 6
        cursor.execute("""
        SELECT s.song_id, MAX(lt.title) AS title
        FROM songs s
        JOIN localized_titles lt ON s.song_id = lt.song_id
        WHERE lt.title REGEXP '^[A-Za-z ]+$'
        GROUP BY s.song_id
        HAVING COUNT(lt.title) = 1
        ORDER BY RAND()
        LIMIT %s;
        """,(n,))
        result = cursor.fetchall()
        for song_id, title in result:
            self.songs.append(song_id)
            self.answer.append(title)
            self.state.append(re.sub('[a-zA-Z]', '\\*', title))
        await self.currState(ctx, 'Game Start!\n')

    async def currState(self, ctx, note='Current Game:\n'):
        msg = [note]
        msg.append(f'Viewed: {','.join(self.viewed)}')
        for i, song in enumerate(self.state, 1):
            msg.append(f'{i}: {song}')
        # for testing purpose
        for i, song in enumerate(self.answer, 1):
            msg.append(f'{i}: {song}')

        await ctx.send('\n'.join(msg))

    def view(self, s, user):
        if not len(s) == 1:
            return 'The Argument MUST Be A Single Character'
        if s in self.viewed:
            return 'Character Already Viewed'
        self.viewed.append(s)
        for i, song in enumerate(self.answer):
            for j, char in enumerate(song):
                if char == s:
                    self.state[i][j] = s

        return f'{user.display_name} viewed {s}'

async def setup(bot):
    await bot.add_cog(Play(bot))