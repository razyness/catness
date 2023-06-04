import discord
import asyncio

from discord.ext import commands

from data import config

class Client(commands.AutoShardedBot):
    def __init__(self, intents, command_prefix, allowed_mentions):
        super().__init__(
            intents=intents,
            command_prefix=command_prefix,
            allowed_mentions=allowed_mentions
        )
        self.command_prefix = config["prefix"]


intents = discord.Intents.all()
prefix = config["prefix"]
mentions = discord.AllowedMentions(roles=False, users=True, everyone=False)
ce = Client(intents=intents, command_prefix=prefix, allowed_mentions=mentions)


async def load():
    await ce.load_extension('jishaku')
    await ce.load_extension('cogs.events')
    print('🟪 initial extensions loaded')


asyncio.run(load())
ce.run(config["TOKEN"])
