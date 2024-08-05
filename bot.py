import discord
import logging
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='lowiro-', intents=intents)

dir_path = os.path.dirname(os.path.realpath(__file__))
cog_directory = os.path.join(dir_path, 'cogs')
async def load_cogs():
    for filename in os.listdir(cog_directory):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')

@bot.event
async def on_ready():
    await load_cogs()
    print(f'We have logged in as {bot.user}')

@bot.command()
@commands.is_owner()
async def load(ctx, extension):
    try:
        await bot.load_extension(f'cogs.{extension}')
        await ctx.send(f'Loaded {extension}')
    except Exception as e:
        await ctx.send(f'Failed to load {extension} \n{type(e).__name__}: {e}')

@bot.command()
@commands.is_owner()
async def unload(ctx, extension):
    try:
        await bot.unload_extension(f'cogs.{extension}')
        await ctx.send(f'Unloaded {extension}')
    except Exception as e:
        await ctx.send(f'Failed to unload {extension} \n{type(e).__name__}: {e}')

@bot.command()
@commands.is_owner()
async def reload(ctx, extension):
    try:
        await bot.unload_extension(f'cogs.{extension}')
        await bot.load_extension(f'cogs.{extension}')
        await ctx.send(f'Reloaded {extension}')
    except Exception as e:
        await ctx.send(f'Failed to reload {extension} \n{type(e).__name__}: {e}')

@bot.command()
@commands.is_owner()
async def reload_all(ctx):
    for filename in os.listdir(cog_directory):
        if filename.endswith('.py'):
            try:
                await bot.unload_extension(f'cogs.{filename[:-3]}')
                await bot.load_extension(f'cogs.{filename[:-3]}')
            except Exception as e:
                await ctx.send(f'Failed to reload {filename[:-3]} \n{type(e).__name__}: {e}')
    await ctx.send('Reloaded all cogs')

handler = logging.FileHandler(filename=f'discord.log', encoding='utf-8', mode='w')
bot.run(TOKEN, log_handler=handler)