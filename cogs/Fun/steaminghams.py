from discord import app_commands
from discord.ext import commands
from discord import ui

import toml
import discord
from sakana import STEAM_API_KEY
import requests

#		if user == discord.User:
#			user_db = toml.load("./cogs/steam.json")
#			if user.id not in user_db:
#				await interaction.response.send_message(f"`{str(user)}` has not linked their steam account to the bot.", ephemeral=True)
#				return

# Button views
class steamProfile(ui.View):
	def __init__(self, user):
		super().__init__()
		self.value = None
		self.user = user

def getID(user):
	r = requests.get(f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={STEAM_API_KEY}&vanityurl={user}")
	userID = r.json()["response"]["steamid"]
	return userID

def mainPage(user):

	userID = getID(user)

	r1 = requests.get(f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM_API_KEY}&steamids={userID}")
	userInfo = r1.json()["response"]["players"][0]

	embed=discord.Embed()
	embed.title=userInfo["personaname"]
	embed.url=userInfo["profileurl"]
	embed.color = 0x66c0f4
	embed.set_thumbnail(url=userInfo["avatarfull"])
	return embed

#main interaction veiw
class Steam(commands.Cog):

	def __init__(self, ce):
		super().__init__()
		self.ce = ce

	# WIP
	@app_commands.command(name="steam", description="View steam profiles :)")
	async def steam(self, interaction, user:str):
		try:
			await interaction.response.send_message(embed=mainPage(user))
		except Exception as e:
			await interaction.response.send_message(e)

		

async def setup(ce):
	await ce.add_cog(Steam(ce))
