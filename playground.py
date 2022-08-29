import discord
import os
import asyncio
import logging
from discord.ext import commands

prefix = '.'

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(
    filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter(
    '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

ce = commands.Bot(command_prefix=prefix, intents=intents)


@ce.event
async def on_message(message):
    if 'oh' in message.content and message.author.bot is False:
        await message.channel.send('oh')
    await ce.process_commands(message)

async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await ce.load_extension(f'cogs.{filename[:-3]}')
    await ce.load_extension('jishaku')


asyncio.run(load())
ce.run('OTQzOTQyMzU2MTQxNDgyMDc0.GUmEbN.tepFChtGTRHRByHzWR7Ey0Upm2XjGRTpugfJQs')
