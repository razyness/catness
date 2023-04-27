from discord import app_commands
from discord.ext import commands
from discord import ui

import aiosqlite
import discord

from utils.http import HTTP

from data import config, Data

STEAM = config["STEAM"]
http = HTTP()

class steamProfile(ui.View):
	def __init__(self, user):
		super().__init__()
		self.value = None
		self.user = user


async def getID(user):
	ResolveVanity = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={STEAM}&vanityurl={user}"
	userID = await http.get(url=ResolveVanity)
	if userID["response"]["success"] == 1:
		return userID["response"]["steamid"]
	return user


async def mainPage(user):
	userID = await getID(user)

	PlayerSummaries = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM}&steamids={userID}"
	PlayerLevel = f"https://api.steampowered.com/IPlayerService/GetSteamLevel/v1/?key={STEAM}&steamid={userID}"

	userInfo = await http.get(url=PlayerSummaries)
	userLevel = await http.get(url=PlayerLevel)

	userInfo = userInfo["response"]["players"][0]
	embed = discord.Embed(
		description=f"`{userInfo['profileurl'].split('/')[4]}` is level `{userLevel['response']['player_level']}`")
	
	embed.add_field(name="Member since", value="<t:1640450437:R>")
	name = "Status"
	statuscolor = 0x66c0f4

	if userInfo["personastate"] == 1:
		lastseen = "`Online`"
		statuscolor = 0x2cc956
	elif userInfo["personastate"] == 0:
		name = "Last seen"
		lastseen = f'<t:{userInfo["lastlogoff"]}:R>'
	elif userInfo["personastate"] == 2:
		lastseen = "`Busy`"
		statuscolor = 0xc92c2c
	elif userInfo["personastate"] == 3:
		lastseen = "`Away`"
		statuscolor = 0xdeaf2c
	elif userInfo["personastate"] == 4:
		lastseen = "`Snooze`"
		statuscolor = 0x223c7d
	else:
		lastseen = "`Hidden/Unavailable`"

	embed.add_field(name=name, value=lastseen)
	if "gameextrainfo" in userInfo:
		embed.add_field(
			name="In-game", value=f"[{userInfo['gameextrainfo']}](https://store.steampowered.com/app/{userInfo['gameid']})", inline=False)
		embed.set_image(
			url=f"https://cdn.cloudflare.steamstatic.com/steam/apps/{userInfo['gameid']}/header.jpg")

	embed.title = userInfo["personaname"]
	embed.url = userInfo["profileurl"]
	embed.color = statuscolor
	embed.set_thumbnail(url=userInfo["avatarfull"])
	return embed


class Steam(commands.Cog):

	def __init__(self, ce):
		super().__init__()
		self.ce = ce

	@app_commands.command(name="steam", description="View steam profiles :)")
	@app_commands.describe(user="The user's vanity, steam id or discord mention if they linked their account",
						   ephemeral="Whether the result will be visible to you (True) or everyone else (False)")
	async def steam(self, interaction, user: str = None, ephemeral: bool = False):
		if user is None or user.startswith("<@"):
			if user is None:
				user_id = interaction.user.id
				g = "You haven't"
			elif user.startswith("<@"):
				user_id = int(user[2:-1])
				g = f"<@{user_id}> hasn't"
				if user_id == interaction.user.id:
					g = "You haven't"
			try:
				social_data = await Data.load_db(table="profiles", user_id=user_id)
				if social_data['steam'] is None:
					raise Exception
				user = social_data['steam']
			except:
				await interaction.response.send_message(f"{g} linked a `Steam` account! Run </link:1080264642569441380> to do so", ephemeral=True)
				return
		try:
			embed = await mainPage(user)
			await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
		except Exception as e:
			await interaction.response.send_message(f"I couldn't find the user. Did you use the vanity url of the user? {e}", ephemeral=True)


async def setup(ce):
	await ce.add_cog(Steam(ce))
