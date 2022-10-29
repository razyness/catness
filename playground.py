import os
import asyncio
from discord.ext import commands
from sakana import *

# logger.setLevel(logging.DEBUG)
# logging.getLogger('discord.http').setLevel(logging.INFO)
# handler.setFormatter(formatter)
# logger.addHandler(handler)

intents.members = True
intents.presences = True
intents.message_content = True

ce = commands.Bot(command_prefix=prefix, intents=intents)


async def load():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            try:
                await ce.load_extension(f'cogs.{filename[:-3]}')
                print(f'🟨 {filename} was loaded')
            
            except Exception as e:
                print(f'🟥 {filename} was not loaded - {e}')

    await ce.load_extension('jishaku')
    print('🟪 all extensions loaded!!')


asyncio.run(load())
ce.run(TOKEN, log_handler=None)
