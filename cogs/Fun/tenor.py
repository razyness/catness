from discord import app_commands
from discord.ext import commands

import aiohttp
import random
import toml

config = toml.load("config.toml")
TENOR = config["TENOR"]


class Tenor(commands.Cog):
	def __init__(self, ce):
		super().__init__()
		self.ce = ce

	@app_commands.command(name="catgif", description="Random Tenor cat gif")
	async def catgif(self, interaction):
		# set the apikey and limit
		apikey = TENOR  # click to set to your apikey
		lmt = 50
		# set the client_key for the integration and use the same value for all API calls
		ckey = "tenor-api"

		variations = ["cats", "kitten gif", "small cat", "cute cat", "loafed cat",
					  "cat jumping", "kitten playing", "the cats", "a cat", "a kitten walking"]

		query = random.choice(variations).replace(" ", "+")

		# get the top 8 GIFs for the search term
		async with aiohttp.ClientSession() as session:
				async with session.get(f"https://tenor.googleapis.com/v2/search?q={query}&key={apikey}&client_key={ckey}&limit={lmt}&random=true") as response:
					result = await response.json()

		result = result["results"][0]["itemurl"]

		await interaction.response.send_message(result)

	@app_commands.command(name="tenor", description="Search through tenor")
	@app_commands.describe(query="The search terms")
	async def tenor(self, interaction, query: str):
		# set the apikey and limit
		apikey = TENOR  # click to set to your apikey
		lmt = 50
		# set the client_key for the integration and use the same value for all API calls
		ckey = "tenor-api"

		query = query.replace(" ", "+")
		# get the top 8 GIFs for the search term
		async with aiohttp.ClientSession() as session:
				async with session.get(f"https://tenor.googleapis.com/v2/search?q={query}&key={apikey}&client_key={ckey}&limit={lmt}&random=true") as response:
					result = await response.json()

		result = result["results"][0]["itemurl"]

		await interaction.response.send_message(result)

	@app_commands.command(name="woody", description="woody from Neighbours from Hell")
	async def woody(self, inter):
		await inter.response.send_message("https://github.com/razyness/catness/raw/main/woody.jpg")


async def setup(ce):
	await ce.add_cog(Tenor(ce))
