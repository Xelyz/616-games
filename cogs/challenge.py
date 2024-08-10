import discord
import random
from discord.ext import commands
from discord import ButtonStyle, SelectOption
from discord.ui import View, Select

OPTIONS = ('Rock', 'Paper', 'Scissors', 'Hikari', 'Tairitsu')
RESULTS = [
    [0, -1, 1, 1, -1],
    [1, 0, -1, 1, -1],
    [-1, 1, 0, -1, 1],
    [-1, -1, 1, 0, 1],
    [1, 1, -1, -1, 0],
]
games = {}

class Challenge(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help='initiate a rock paper scissors challenge')
    async def challenge(self, ctx):
        view = SelectView()
        await ctx.send('Select to start a challenge', view=view)

def battle(object1, object2):
    a = OPTIONS.index(object1)
    b = OPTIONS.index(object2)
    return RESULTS[a][b]


class Dropdown(Select):
    def __init__(self, author):
        # Set the options that will be presented inside the dropdown
        options = [SelectOption(label=option) for option in OPTIONS]
        random.shuffle(options)
        super().__init__(placeholder="What do you play?", options=options)
        self.callback = self.player2 if author else self.player1
        self.author = author

    async def player1(self, interaction):
        # This function gets called when the challenge sender selects an option
        user = interaction.user
        games[user.id] = self.values[0]
        view = ChallengeView(user)
        await interaction.response.edit_message(content=f'{user.display_name} initiated a challenge!', view=view)

    async def player2(self, interaction):
        # This function gets called when the challenger selects an option
        object1 = games.get(self.author.id, False)
        if not object1:
            await interaction.response.edit_message(content=f'Game not found', view=None, delete_after=3)
        object2 = self.values[0]
        res = battle(object1, object2)

        if res == 1:
            msg = f'{object1} beats {object2}, {self.author.display_name} wins!'
        elif res == -1:
            msg = f'{object2} beats {object1}, {interaction.user.display_name} wins!' 
        else:
            msg = f'{object1} vs. {object2}, It\'s a Tie...'
        
        await interaction.response.edit_message(content=f'Played {object2}', view=None, delete_after=3)
        await interaction.followup.send(
            f'{self.author.display_name} played {object1}, {interaction.user.display_name} played {object2}\n{msg}'
            )
        

class ChallengeView(View):
    def __init__(self, author):
        super().__init__()
        self.author = author

    @discord.ui.button(label="Accept!", style=ButtonStyle.primary, custom_id="accept_challenge")
    async def button_click(self, interaction, button):
        view = SelectView(self.author)
        await interaction.response.edit_message(content=f"{interaction.user.display_name} accepted the challenge from {self.author.display_name}!", view=None)
        await interaction.followup.send('', view=view, ephemeral=True)


class SelectView(View):
    def __init__(self, author=None):
        '''
        author: the person who initiated the challenge
        '''
        super().__init__()
        self.add_item(Dropdown(author))

async def setup(bot):
    await bot.add_cog(Challenge(bot))