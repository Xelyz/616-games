import discord
from discord.ext import commands
from discord.ui import View
from discord import ButtonStyle
import os
import mysql.connector
import re
from dotenv import load_dotenv

#next: manage the start of the game after clicking the colab or compete button.

load_dotenv()
PWD = os.getenv('PASSWORD')
# Establish connection
conn = mysql.connector.connect(user='discordbot', password=PWD, host='localhost', database='arcaeaSongInfo')
cursor = conn.cursor()

def ToLowerCase(arg):
    return arg.lower()

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if ctx.cog is None or ctx.cog.qualified_name != self.__class__.__name__:
            return
        await ctx.send(err)
        raise err

    @commands.group(invoke_without_command=True, help='Play a mini game!')
    async def dplay(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Please enter valid game name. Avaiable Games can be viewed with "lowiro-games"')

    @dplay.command(help='Start a game of Hangman')
    async def hangman(self, ctx):
        channel_id = ctx.channel.id
        if channel_id not in self.games:
            embed = discord.Embed(
                title="Hangman",
                description="**Description**:\nGuess the song title by viewing letters\n\nChoose your mode:",
                color=discord.Color.blue()  # You can change the color as needed
            )
            embed.add_field(name='Colaborative Game', value='play hangman with one song title and 6 life', inline=False)
            embed.add_field(name='Competitive Game', value='play hangman with 6 song title and compete for the highest score', inline=False)
            # self.games[channel_id] = game = Hangman()
            # await game.start(ctx)
            view = ChooseGameModeView(ctx.channel, self)
            msg = await ctx.send(embed=embed, view=view)
            view.msg = msg
        else:
            await ctx.send("A game is already running in this channel!")

    @commands.command(help='List all available games')
    async def dgames(self, ctx):
        await ctx.send('Available Games: Hangman')

    @commands.command(help='Ends the game in the channel')
    async def dend(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in self.games:
            await ctx.send(f'{self.games[channel_id].name} in this channel ended...')
            await self.games[channel_id].endGame(ctx.channel)
            del self.games[channel_id]
        else:
            await ctx.send('There are no games running in this channel...')

    @commands.command(help='Hangman game command. View a character')
    async def dview(self, ctx, s: ToLowerCase):
        channel_id = ctx.channel.id
        if channel_id in self.games:
            game = self.games[channel_id]

            if not isinstance(game, Hangman):
                await ctx.send(f'Invalid Command: {game.name} is running instead of Hangman...')
                return
            
            if not game.playing:
                await ctx.send(f'Invalid Command: {game.name} is still waiting to start')
                return
            
            msg = game.view(s, ctx.author)
            await game.currState(ctx, msg)
            if game.isOver() == -1:
                await ctx.send('Game Over!')
                await game.endGame(ctx.channel)
                del self.games[channel_id]
            elif game.isOver() == 1:
                await ctx.send('Game Completed! Horray!')
                await game.endGame(ctx.channel)
                del self.games[channel_id]
        else:
            await ctx.send('Hangman is not running. Perhaps you want to start a game?')

class ChooseGameModeView(View):
    def __init__(self, channel, cog):
        # Timeout set to 20 seconds
        super().__init__(timeout=20)
        self.channel = channel
        self.cog = cog

    async def on_timeout(self):
        if hasattr(self, 'msg'):
            await self.msg.edit(view=None)  # Update the message to show the disabled buttons

    @discord.ui.button(label="Colab", style=ButtonStyle.primary, custom_id="colab")
    async def colab(self, interaction, button):
        # Optionally disable the button immediately after it's pressed
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        self.cog.games[interaction.channel_id] = game = Hangman()
        await game.start(self.channel)

    @discord.ui.button(label="Compete", style=ButtonStyle.primary, custom_id="compete")
    async def compete(self, interaction, button):
        # Optionally disable the button immediately after it's pressed
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)

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
        self.players = []
        self.life = 6
        self.dmg = 1
        self.mode = 1 # 1 if colab, 2 if compete
        self.playing = False

    async def start(self, channel):
        if self.mode == 1: 
            n = 1
        else:
            n = 6
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
        for song_id, title in result:
            self.songs.append(song_id)
            self.answer.append(title)
            self.state.append([None if char != ' ' else char for char in title])
            self.completed.append(False)
        await self.currState(channel, 'Game Start!\nUse lowiro-view <character> to play\n')
        self.playing = True

    def isOver(self):
        if self.life <= 0:
            return -1
        if all(self.completed):
            return 1
        return 0

    async def endGame(self, channel):
        msg = ["Reveal answer:"]
        for i, song in enumerate(self.answer, 1):
            msg.append(f'{i}: {song}')
        await channel.send('\n'.join(msg))

    async def currState(self, channel, note='Current Game:\n'):
        msg = [note]
        msg.append(f'Viewed: {','.join(self.viewed)}')
        for i, song in enumerate(self.state, 1):
            if self.completed[i-1]:
                msg.append(f'{i}: ~~{''.join(song)}~~')
            else:
                msg.append(f'{i}: {''.join('\\*' if c == None else c for c in song)}')
        msg.append(f'Life: {self.life}')
        await channel.send('\n'.join(msg))

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
    await bot.add_cog(Dev(bot))