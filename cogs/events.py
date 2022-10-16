import discord
from discord.ext import commands


class Events(commands.Cog):
	def __init__(self, ce):
		self.ce = ce

	@commands.Cog.listener()
	async def on_ready(self):

		await self.ce.change_presence(activity=discord.Activity(
			type=discord.ActivityType.watching, name="me i'm razyness"))

		print(f"Logged in as {self.ce.user} with a {round(self.ce.latency * 1000)}ms delay")

	@commands.Cog.listener()
	async def on_message(self, message):
		if 'oh' in message.content and message.author.bot is False:
			await message.channel.send('oh')


async def setup(ce):
	await ce.add_cog(Events(ce))
