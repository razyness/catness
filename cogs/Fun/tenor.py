from discord import app_commands
from discord.ext import commands

import aiohttp
import random

from utils import config

TENOR = config["TENOR"]


class Tenor(commands.Cog):
	"""Various commands using the Tenor API, Tenor is a gif website!!"""
	def __init__(self, bot):
		super().__init__()
		self.bot = bot

	@app_commands.command(name="catgif", description="Random Tenor cat gif")
	async def catgif(self, interaction):
		apikey = TENOR
		lmt = 50
		
		ckey = "tenor-api"

		variations = ["cats", "kitten gif", "small cat", "cute cat", "loafed cat",
					  "cat jumping", "kitten playing", "the cats", "a cat", "a kitten walking"]

		query = random.choice(variations).replace(" ", "+")


		async with aiohttp.ClientSession() as session:
				async with session.get(f"https://tenor.googleapis.com/v2/search?q={query}&key={apikey}&client_key={ckey}&limit={lmt}&random=true") as response:
					result = await response.json()

		result = result["results"][0]["itemurl"]

		await interaction.response.send_message(result)

	@app_commands.command(name="tenor", description="Search through tenor")
	@app_commands.describe(query="The search terms")
	async def tenor(self, interaction, query: str):
		apikey = TENOR
		lmt = 50
		
		ckey = "tenor-api"

		query = query.replace(" ", "+")
		
		async with aiohttp.ClientSession() as session:
				async with session.get(f"https://tenor.googleapis.com/v2/search?q={query}&key={apikey}&client_key={ckey}&limit={lmt}&random=true") as response:
					result = await response.json()

		result = result["results"][0]["itemurl"]

		await interaction.response.send_message(result)

	@app_commands.command(name='reaction', description='Live slug reaction')
	async def reaction(self, interaction):
		try:
			async with self.bot.web_client.get(f"https://tenor.googleapis.com/v2/search?q=live-reaction&key={self.bot.config['TENOR']}&client_key=tenor-api&limit=50&random=true") as r:
				result = await r.json()
				result = result["results"][0]["itemurl"]
				await interaction.response.send_message(result)
		except Exception as e:
			print(e)

async def setup(bot):
	await bot.add_cog(Tenor(bot))
