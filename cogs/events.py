import discord
import os
import random
import asyncio
from discord.ext import commands, tasks


class Events(commands.Cog):
	def __init__(self, ce):
		self.ce = ce

	async def setup_hook(self):
		await self.tree.sync(guild=discord.Object(id=904460336118267954))

	@tasks.loop(seconds=20.0)
	async def presences(self):
		
		catchphrases = ["Important information", "Loading", "Something beautiful is coming", "Thinking outside the box",
		"Vague rumbling", "Getting our load on", "Pushing it to the limit",
		"Connecting to LittleBigPlanet Online", "Profile is corrupt!", "Putting everything in order",
		"Do not forget...", "Ironing out the creases"]

		await self.ce.change_presence(status=discord.Status.online, activity=discord.Activity(
			type=discord.ActivityType.watching, name=random.choice(catchphrases)))

	@commands.Cog.listener()
	async def on_ready(self):


		await self.ce.change_presence(status=discord.Status.idle, activity=discord.Activity(
			type=discord.ActivityType.watching, name='loading up...'))

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
		
		if not self.presences.is_running():
			self.presences.start()

		print(f"🟩 Logged in as {self.ce.user} with a {round(self.ce.latency * 1000)}ms delay")
		
									
	@commands.Cog.listener()
	async def on_message(self, message):
		if 'oh' in message.content and message.author.bot is False:
			await message.channel.send('oh')
	

async def setup(ce):
	await ce.add_cog(Events(ce))
