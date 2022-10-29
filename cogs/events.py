import discord
import os
from asyncio import sleep
from discord.ext import commands


class Events(commands.Cog):
	def __init__(self, ce):
		self.ce = ce

	async def setup_hook(self):
		await self.tree.sync(guild=discord.Object(id=904460336118267954))

	@commands.Cog.listener()
	async def on_ready(self):

		await self.ce.change_presence(activity=discord.Activity(
			type=discord.ActivityType.watching, name="me i'm razyness"))

		try:
			synced = await self.ce.tree.sync()
			print(f"🔁 synced {len(synced)} slash commands")
		except Exception as e:
			print(e)
					
		print(f"🟩 Logged in as {self.ce.user} with a {round(self.ce.latency * 1000)}ms delay")
		


	@commands.Cog.listener()
	async def on_message(self, message):
		if 'oh' in message.content and message.author.bot is False:
			await message.channel.send('oh')


async def setup(ce):
	await ce.add_cog(Events(ce))
