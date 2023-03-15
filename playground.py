import discord
import asyncio
from discord.ext import commands

intents = discord.Intents.all()
from data.__init__ import config


class Client(commands.Bot):
    def __init__(self):
        super().__init__(intents=intents, command_prefix=config["prefix"])
        self.command_prefix = config["prefix"]

ce = Client()

async def load():
    await ce.load_extension('jishaku')
    await ce.load_extension('cogs.events')
    print('🟪 initial extensions loaded')


asyncio.run(load())
ce.run(config["TOKEN"])
