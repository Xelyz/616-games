import discord
from discord.ext import commands
import os
import mysql.connector
from mysql.connector import Error
import re
from dotenv import load_dotenv

load_dotenv()
PWD = os.getenv('PASSWORD')

def connect():
    # Establish connection
    global conn
    conn = mysql.connector.connect(user='discordbot', password=PWD, host='localhost', database='arcaeaSongInfo')

def ToLowerCase(arg):
    return arg.lower()

class Play(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}
        connect()

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if ctx.cog is None or ctx.cog.qualified_name != self.__class__.__name__:
            return
        await ctx.send(err)
        raise err

    @commands.group(invoke_without_command=True, help='Play a mini game!')
    async def play(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Please enter valid game name. Avaiable Games can be viewed with "lowiro-games"')

    @play.command(help='Start a game of Hangman')
    async def hangman(self, ctx):
        channel_id = ctx.channel.id
        if channel_id not in self.games:
            self.games[channel_id] = game = Hangman()
            await game.startGame(ctx)
        else:
            await ctx.send("A game is already running in this channel!")

    @commands.command(help='List all available games')
    async def games(self, ctx):
        await ctx.send('Available Games: Hangman')

    @commands.command(help='Ends the game in the channel')
    async def end(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in self.games:
            await ctx.send(f'{self.games[channel_id].name} in this channel ended...')
            await self.games[channel_id].endGame(ctx)
            del self.games[channel_id]
        else:
            await ctx.send('There are no games running in this channel...')

    @commands.command(help='Hangman game command. View a character')
    async def view(self, ctx, s: ToLowerCase):
        channel_id = ctx.channel.id
        if channel_id in self.games:
            game = self.games[channel_id]
            if not isinstance(game, Hangman):
                await ctx.send(f'Invalid Command: {game.name} is running instead of Hangman...')
            msg = game.view(s, ctx.author)
            await game.currState(ctx, msg)
            if game.isOver() == -1:
                await ctx.send('Game Over!')
                await game.endGame(ctx)
                del self.games[channel_id]
            elif game.isOver() == 1:
                await ctx.send('Game Completed! Horray!')
                await game.endGame(ctx)
                del self.games[channel_id]
        else:
            await ctx.send('Hangman is not running. Perhaps you want to start a game?')

class Hangman():
    def __init__(self):
        self.name = 'Hangman'
        # answer is a list of strings which contains the Correct song title
        self.answer = []
        # state is a list of list of chars which shows whether the character is viewed
        self.state = []
        self.songs = []
        self.viewed = []
        self.completed = []
        self.life = 6
        self.dmg = 1

    async def startGame(self, ctx):
        n = 1

        if conn is None or not conn.is_connected():
            connect()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT song_id, title
        FROM (
            SELECT s.song_id, MAX(lt.title) AS title
            FROM songs s
            JOIN localized_titles lt ON s.song_id = lt.song_id
            GROUP BY s.song_id
            HAVING COUNT(lt.title) = 1
        ) AS subquery
        WHERE title REGEXP '^[A-Za-z ]+$'
        ORDER BY RAND()
        LIMIT %s;
        """,(n,))
        result = cursor.fetchall()
        cursor.close()

        for song_id, title in result:
            self.songs.append(song_id)
            self.answer.append(title)
            self.state.append([None if char != ' ' else char for char in title])
            self.completed.append(False)
        await self.currState(ctx, 'Game Start!\nUse lowiro-view <character> to play\n')

    def isOver(self):
        if self.life <= 0:
            return -1
        if all(self.completed):
            return 1
        return 0

    async def endGame(self, ctx):
        msg = ["Reveal answer:"]
        for i, song in enumerate(self.answer, 1):
            msg.append(f'{i}: {song}')
        await ctx.send('\n'.join(msg))

    async def currState(self, ctx, note='Current Game:\n'):
        msg = [note]
        msg.append(f'Viewed: {','.join(self.viewed)}')
        for i, song in enumerate(self.state, 1):
            if self.completed[i-1]:
                msg.append(f'{i}: ~~{''.join(song)}~~')
            else:
                msg.append(f'{i}: {''.join('\\*' if c == None else c for c in song)}')
        msg.append(f'Life: {self.life}')
        await ctx.send('\n'.join(msg))

    def view(self, s, user):
        if not len(s) == 1:
            return 'The Argument MUST Be A Single Character\n'
        if s in self.viewed:
            return 'Character Already Viewed\n'
        self.viewed.append(s)
        dmg = self.dmg
        for i, song in enumerate(self.answer):
            if self.completed[i]:
                continue
            for j, char in enumerate(song):
                if char.lower() == s and self.state[i][j] == None:
                    self.state[i][j] = char
                    dmg = 0
                    if None not in self.state[i]:
                        self.completed[i] = True
                    
        self.life -= dmg
        return f'{user.display_name} viewed {s}\n'

async def setup(bot):
    await bot.add_cog(Play(bot))