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


class Client(commands.Bot):
	def __init__(self):
		super().__init__(intents=discord.Intents.all(), command_prefix=prefix)
		self.command_prefix = prefix

ce = Client()


async def load():

	await ce.load_extension('jishaku')
	await ce.load_extension('cogs.events')
	print('🟪 initial extensions loaded')


asyncio.run(load())
ce.run(TOKEN, log_handler=None)
