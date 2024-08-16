from typing import Coroutine
import discord
from discord.ext import commands
from discord.ui import View
from discord import ButtonStyle
from .utils.query import Query

cursor = Query()

def ToLowerCase(arg):
    return arg.lower()

def insert(song_id, alias):
    cursor.execute('''
INSERT INTO alias (song_id, title)
VALUES (%s, %s)
''', (song_id, alias))

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
    async def add_alias(self, ctx, song: ToLowerCase, alias):
        result = cursor.execute("""
            SELECT t.song_id, t.title, 
            (MATCH(t.title) AGAINST(%s) + 
            IF(LOWER(t.title) = %s, 100, 0)) AS relevance
            FROM localized_titles t
            WHERE MATCH(t.title) AGAINST(%s)
            ORDER BY relevance DESC;
            """,(song, song, song))
        
        if result:
            result = result[0]
            song_id = result[0]
            title = result[1]

            result = cursor.execute('''
SELECT title
FROM alias
WHERE LOWER(title) = %s
UNION   
SELECT title
FROM localized_titles
WHERE LOWER(title) = %s
''', (alias.lower(), alias.lower()))
            
            if result:
                await ctx.send("Alias already added")
            else:
                view = ConfirmView(insert, song_id, alias)
                msg = await ctx.send(f"Adding alias **{alias}** to song **{title}**.\n*Timeout in 5 seconds*", view=view)
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
            result = cursor.execute("""
            SELECT t.song_id, t.title, 
            (MATCH(t.title) AGAINST(%s) + 
            IF(LOWER(t.title) = %s, 100, 0)) AS relevance, 
            (MATCH(alias.title) AGAINST(%s) + 
            IF(LOWER(alias.title) = %s, 100, 0)) AS alias_relevance
            FROM localized_titles t
            LEFT JOIN alias ON t.song_id = alias.song_id
            WHERE MATCH(t.title) AGAINST(%s) OR MATCH(alias.title) AGAINST(%s)
            ORDER BY GREATEST(relevance, alias_relevance) DESC;
            """,(song, song, song, song, song, song))

            if result:
                result = result[0]
                song_id = result[0]
                title = result[1]
                url, id, artist, bpm, set_name, side, version = cursor.execute("""
                SELECT url, id, artist, bpm, set_name, side, version
                FROM songs 
                WHERE song_id = %s;
                """,(song_id,))[0]

                difficulties = cursor.execute("""
                SELECT rating_class, rating, chart_constant, refer_to
                FROM difficulties 
                WHERE song_id = %s;
                """,(song_id,))

                display = []
                for rating_class, rating, chart_constant, refer_to in difficulties:
                    if refer_to:
                        res = cursor.execute("""
                        SELECT rating_class, rating, chart_constant
                        FROM difficulties
                        WHERE song_id = %s AND rating_class = %s;
                        """,(refer_to, rating_class))
                        if res:
                            rating_class, rating, chart_constant = res[0]

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
                    const = f' ({chart_constant})' if chart_constant >= 9.0 else ''

                    display.append(f'[{cls}](https://www.youtube.com/results?search_query=arcaea+{id}+{cls}): {rating}{plus}{const}')

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
                    title=title,
                    color=color  # You can change the color as needed
                )
                embed.add_field(name='Artist: ', value=artist, inline=True)
                embed.add_field(name='BPM: ', value=bpm, inline=True)
                embed.add_field(name='Version: ', value=version, inline=True)
                embed.add_field(name='', value=f'**Side:** {side}', inline=False)
                embed.add_field(name='Level', value=display, inline=False)

                embed.set_thumbnail(url=url)

                await ctx.send(embed=embed)
            else:
                await ctx.send('''
Cannot find the song. You might have a typo or the phrase is not recognized.
You can use lowiro-add-alias <song_title> <alias> to add alias
''')

async def setup(bot):
    await bot.add_cog(Info(bot))