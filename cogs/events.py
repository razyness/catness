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

		await self.ce.change_presence(status=discord.Status.idle, activity=discord.Activity(
			type=discord.ActivityType.watching, name="loading up..."))

		for filename in os.listdir('./cogs'):
			if filename.endswith('.py') and not filename.startswith('events'):
				try:
					await self.ce.load_extension(f'cogs.{filename[:-3]}')
					print(f'🟨 {filename} was loaded')

				except Exception as e:
					print(f'🟥 {filename} was not loaded - {e}')
		
		print('🟪 all extensions loaded!!')

		try:
			synced = await self.ce.tree.sync()
			print(f"🔁 synced {len(synced)} slash commands")
		except Exception as e:
			print(e)
		
		await self.ce.change_presence(activity=discord.Activity(
			type=discord.ActivityType.watching, name="me i'm razyness"))
		print(f"🟩 Logged in as {self.ce.user} with a {round(self.ce.latency * 1000)}ms delay")
		


	@commands.Cog.listener()
	async def on_message(self, message):
		if 'oh' in message.content and message.author.bot is False:
			await message.channel.send('oh')


async def setup(ce):
	await ce.add_cog(Events(ce))
