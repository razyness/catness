import discord
import asyncio
from discord.ext import commands
import toml

intents = discord.Intents.all()
config = toml.load("config.toml")


class Client(commands.Bot):
    def __init__(self):
        super().__init__(intents=intents, command_prefix=config["prefix"])
        self.command_prefix = config["prefix"]


ce = Client()


async def load():
    await ce.load_extension('jishaku')
    await ce.load_extension('Cogs.events')
    print('🟪 initial extensions loaded')


asyncio.run(load())
ce.run(config["TOKEN"])
