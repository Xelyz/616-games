import discord
from discord.ext import commands
from discord.ui import View
from discord import ButtonStyle
from ..query import Query

#next: scoring

games = {}

cursor = Query()

def ToLowerCase(arg):
    return arg.lower()

class Dev(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
        if channel_id not in games:
            embed = discord.Embed(
                title="Hangman",
                description="**Description**:\nGuess the song title by viewing letters\n\nChoose your mode:",
                color=discord.Color.blue()  # You can change the color as needed
            )
            embed.add_field(name='Colaborative Game', value='play hangman with one song title and 6 life', inline=False)
            embed.add_field(name='Competitive Game', value='play hangman with 6 song title and compete for the highest score **under dev**', inline=False)
            # self.games[channel_id] = game = Hangman()
            # await game.start(ctx)
            games[channel_id] = Hangman()
            view = ChooseGameModeView(channel_id)
            msg = await ctx.send(embed=embed, view=view)
            view.msg = msg
        else:
            await ctx.send("A game is already running in this channel!")

    @commands.command(name='dgames', help='List all available games')
    async def lsgames(self, ctx):
        await ctx.send('Available Games: Hangman')

    @commands.command(help='Ends the game in the channel')
    async def dend(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in games:
            game = games[channel_id]
            del games[channel_id]
            await ctx.send(f'{game.name} in this channel ended...')
            await game.endGame()
        else:
            await ctx.send('There are no games running in this channel...')

    @commands.command(help='Hangman game command. View a character')
    async def dview(self, ctx, s: ToLowerCase):
        channel_id = ctx.channel.id
        if channel_id in games:
            game = games[channel_id]

            if not isinstance(game, Hangman):
                await ctx.send(f'Invalid Command: {game.name} is running instead of Hangman...')
                return
            
            if game.waiting:
                await ctx.send(f'Invalid Command: {game.name} is still waiting to start')
                return
            
            msg = game.view(s, ctx.author)
            await game.currState(msg)
            if game.isOver() == -1:
                await ctx.send('Game Over!')
                await game.endGame()
                del games[channel_id]
            elif game.isOver() == 1:
                await ctx.send('Game Completed! Horray!')
                del games[channel_id]
        else:
            await ctx.send('Hangman is not running. Perhaps you want to start a game?')

    @commands.command(help='Hangman game command. View a whole title')
    async def dviewall(self, ctx, *, s: ToLowerCase):
        channel_id = ctx.channel.id
        if channel_id in games:
            game = games[channel_id]

            if not isinstance(game, Hangman):
                await ctx.send(f'Invalid Command: {game.name} is running instead of Hangman...')
                return
            
            if game.waiting:
                await ctx.send(f'Invalid Command: {game.name} is still waiting to start')
                return
            
            msg = game.viewall(s, ctx.author)
            await game.currState(msg)
            if game.isOver() == -1:
                await ctx.send('Game Over!')
                await game.endGame()
                del games[channel_id]
            elif game.isOver() == 1:
                await ctx.send('Game Completed! Horray!')
                del games[channel_id]
        else:
            await ctx.send('Hangman is not running. Perhaps you want to start a game?')

    @commands.command(help='Start whatever game that is waiting for other players in this channel')
    async def dstart(self, ctx):
        channel_id = ctx.channel.id
        if channel_id in games:
            game = games[channel_id]

            if game.waiting:
                await game.start()
                return
            
        await ctx.reply("There are no games to start!")

class ChooseGameModeView(View):
    def __init__(self, channel_id):
        # Timeout set to 20 seconds
        super().__init__(timeout=20)
        self.channel_id = channel_id

    async def on_timeout(self):
        game = games[self.channel_id]
        if game.mode == 0:
            del games[self.channel_id]
        if hasattr(self, 'msg'):
            await self.msg.edit(view=None)  # Update the message to show the disabled buttons

    @discord.ui.button(label="Colab", style=ButtonStyle.primary, custom_id="colab")
    async def colab(self, interaction, button):
        # Optionally disable the button immediately after it's pressed
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        games[interaction.channel_id] = game = Hangman()
        game.channel = interaction.channel
        game.mode = 1
        await game.start()

    @discord.ui.button(label="Compete", style=ButtonStyle.primary, custom_id="compete")
    async def compete(self, interaction, button):
        # Optionally disable the button immediately after it's pressed
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
        games[interaction.channel_id] = game = Hangman()
        game.channel = interaction.channel
        game.mode = 2
        game.players.append(interaction.user)
        game.waiting = True
        view = JoinView(game)
        await game.channel.send(f"{interaction.user.display_name} started a Hangman game!\nClick the button to Join\nuse **lowiro-start** to start game\nAuto start after 2 minutes", view=view)

class JoinView(View):
    def __init__(self, game):
        super().__init__(timeout=120)
        self.game = game

    async def on_timeout(self):
        if self.game.waiting:
            await self.game.start()

    @discord.ui.button(label="Join", style=ButtonStyle.primary, custom_id="join")
    async def join(self, interaction, button):
        if self.game.waiting:
            player = interaction.user
            if player in self.game.players:
                await interaction.response.send_message("You are already in the game!", ephemeral=True)
                return
            
            self.game.players.append(interaction.user)
            await interaction.response.send_message(f"Successfully joined game {self.game.name}!", ephemeral=True)
            return
            
        await interaction.response.send_message("There are no games to join!", ephemeral=True)

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
        self.leader = None
        self.life = 6
        self.dmg = 1
        self.mode = 0 # 1 if colab, 2 if compete
        self.waiting = False
        self.currentPlayer = None # the index of self.players
        self.channel = None

    async def start(self):
        if self.mode == 1: 
            n = 1
        else:
            n = 6
        
        result = cursor.execute("""
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
        
        for song_id, title in result:
            self.songs.append(song_id)
            self.answer.append(title)
            self.state.append([None if char != ' ' else char for char in title])
            self.completed.append(False)
        await self.currState('Game Start!\nUse lowiro-view <character> to play\nUse lowiro-viewall <title> if you know the whole title\n')
        self.waiting = False
        if self.mode == 2:
            self.currentPlayer = 0

    def isOver(self):
        if self.life <= 0:
            return -1
        if all(self.completed):
            return 1
        return 0

    async def endGame(self):
        if self.waiting:
            return
        
        msg = ["Reveal answer:"]
        for i, song in enumerate(self.answer, 1):
            msg.append(f'{i}: {song}')
        await self.channel.send('\n'.join(msg))

    async def currState(self, note='Current Game:\n'):
        msg = [note]
        msg.append(f'Viewed: {','.join(self.viewed)}')
        for i, song in enumerate(self.state, 1):
            if self.completed[i-1]:
                msg.append(f'{i}: ~~{''.join(song)}~~')
            else:
                msg.append(f'{i}: {''.join('\\*' if c == None else c for c in song)}')

        if self.mode == 1:
            msg.append(f'Life: {self.life}')
        
        await self.channel.send('\n'.join(msg))

    def view(self, s, user):
        if not len(s) == 1:
            return 'The Argument MUST Be A Single Character\n'
        if s in self.viewed:
            return 'Character Already Viewed\n'
        if self.mode == 2 and self.players[self.currentPlayer].id != user.id:
            return 'It is not your turn\n'
        
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
                    
        if self.mode == 1:
            self.life -= dmg
            msg = 'Safe!\n' if dmg == 0 else 'Miss!\n'

        if self.mode == 2:
            self.currentPlayer += 1
            self.currentPlayer %= len(self.players)
            msg = f"It's your turn: {self.players[self.currentPlayer].display_name}\n"
        
        return f'{user.display_name} viewed {s}\n' + msg
    
    def viewall(self, s, user):
        if self.mode == 2 and self.players[self.currentPlayer].id != user.id:
            return 'It is not your turn\n'
        
        dmg = self.dmg
        for i, song in enumerate(self.answer):
            if self.completed[i]:
                continue
            if song.lower() == s:
                self.state[i] = song
                dmg = 0
                self.completed[i] = True
                    
        if self.mode == 1:
            self.life -= dmg
            msg = 'Safe!\n' if dmg == 0 else 'Miss!\n'

        if self.mode == 2:
            self.currentPlayer += 1
            self.currentPlayer %= len(self.players)
            msg = f"It's your turn: {self.players[self.currentPlayer].display_name}\n"
        
        return f'{user.display_name} viewed {s}\n' + msg

async def setup(bot):
    await bot.add_cog(Dev(bot))