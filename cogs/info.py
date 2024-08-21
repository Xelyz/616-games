import discord
from discord.ext import commands
from discord.ui import View
from discord import ButtonStyle
from .utils.data import Data
import re

data = Data()
songs = data.songs
alias = data.alias

def ToLowerCase(arg):
    return arg.lower()

def insert(id, name):
    alias[name] = id

class ConfirmView(View):
    def __init__(self, action, *params):
        self.action = action
        self.params = params
        super().__init__(timeout=5)

    async def on_timeout(self):
        await self.msg.edit(view=None)

    @discord.ui.button(label="Confirm", style=ButtonStyle.primary, custom_id="confirm")
    async def confirm(self, interaction, button):
        self.action(*self.params)
        await interaction.response.edit_message(view=None)
        await interaction.channel.send('Alias added successfully!')

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if ctx.cog is None or ctx.cog.qualified_name != self.__class__.__name__:
            return
        await ctx.send(err)
        raise err
    
    @commands.command(name='add-alias', help='lowiro-add-alias "<song>" "<alias>" add alias to a song.\nsong and alias should be in double quote ""')
    async def add_alias(self, ctx, song:ToLowerCase, name:ToLowerCase):
        titles = {song['title']: id for id, song in songs.items()}
        if name in alias or name in map(lambda x: x.lower(), titles.keys()):
            await ctx.send("Alias already added")
            return

        result = sorted([title for title in list(titles.keys())+list(alias.keys()) if re.search(song, title.lower())], key=lambda x: len(x))

        if result:
            result = result[0]
            if result in titles:
                song_id = titles[result]
            else:
                song_id = alias[result]
            view = ConfirmView(insert, song_id, name)
            msg = await ctx.send(f"Adding alias **{alias}** to song **{result}**.\n*Timeout in 5 seconds*", view=view)
            view.msg = msg
        else:
            await ctx.send("Cannot find the song")

    @commands.command(help='arcaea game info')
    async def info(self, ctx, *, song:ToLowerCase = None):
        if song == None:
            await ctx.send('''
"A harmony of Light awaits you in a lost world of musical Conflict."

In a world of white, and surrounded by “memory”, two girls awaken under glass-filled skies.

Arcaea is a mobile rhythm game for both experienced and new rhythm game players alike, blending novel gameplay, immersive sound, and a powerful story of wonder and heartache. Experience gameplay that reflects the story's emotions and events—and progress to unlock more of this unfurling narrative.
Challenging trials can be discovered through play, higher difficulties can be unlocked, and a real-time online mode is available to face off against other players.
''')
        else:
            titles = {song['title']: id for id, song in songs.items()}
            result = sorted([title for title in list(titles.keys())+list(alias.keys()) if re.search(song, title.lower())], key=lambda x: len(x))

            if result:
                result = result[0]
                if result in titles:
                    song_id = titles[result]
                else:
                    song_id = alias[result]
                info = songs[song_id]
                jacket = info.get('jacket')
                name = info.get('name')
                artist = info.get('artist')
                bpm = info.get('bpm')
                set = info.get('set')
                side = info.get('side')
                version = info.get('version')

                difficulties = info.get('difficulties')

                display = []
                for diff in difficulties:
                    rating_class = diff.get('rating_class')
                    rating = diff.get('rating')
                    chart_constant = diff.get('chart_constant')

                    match rating_class:
                        case 0:
                            cls = 'PST'
                        case 1:
                            cls = 'PRS'
                        case 2:
                            cls = 'FTR'
                        case 3:
                            cls = 'BYD'
                        case 4:
                            cls = 'ETR'
                    
                    plus = '+' if chart_constant - int(chart_constant) >= 0.7 else ''
                    const = f' ({chart_constant})' if chart_constant >= 8.0 else ''

                    display.append(f'[{cls}](https://www.youtube.com/results?search_query=arcaea+{name}+{cls}): {rating}{plus}{const}')

                display = ' / '.join(display)

                if side == 0:
                    side = 'light'
                    color = discord.Color.from_rgb(255, 186, 227)
                elif side == 1:
                    side = 'conflict'
                    color = discord.Color.from_rgb(59, 25, 168)
                else:
                    side = '???'
                    color = discord.Color.lighter_grey()

                embed = discord.Embed(
                    title=result,
                    color=color  # You can change the color as needed
                )
                embed.add_field(name='Artist: ', value=artist, inline=True)
                embed.add_field(name='BPM: ', value=bpm, inline=True)
                embed.add_field(name='Version: ', value=version, inline=True)
                embed.add_field(name='', value=f'**Side:** {side}', inline=False)
                embed.add_field(name='Level', value=display, inline=False)

                embed.set_thumbnail(url=jacket)

                await ctx.send(embed=embed)
            else:
                await ctx.send('''
Cannot find the song. You might have a typo or the phrase is not recognized.
You can use lowiro-add-alias <song_title> <alias> to add alias
''')

async def setup(bot):
    await bot.add_cog(Info(bot))