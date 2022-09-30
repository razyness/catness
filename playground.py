import os
import asyncio
from discord.ext import commands
from sakana import *

logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)

intents.members = True
intents.presences = True
intents.message_content = True

ce = commands.Bot(command_prefix=prefix, intents=intents)


async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            print(filename + ' was loaded')
            await ce.load_extension(f'cogs.{filename[:-3]}')
        else:
            print(filename + ' was not loaded')
    await ce.load_extension('jishaku')
    print('all extensions loaded')


asyncio.run(load())
ce.run(TOKEN, log_handler=None)
