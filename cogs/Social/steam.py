from discord import app_commands
from discord.ext import commands
from discord import ui

import json
import discord

STEAM = None


class steamProfile(ui.View):
	def __init__(self, user):
		super().__init__()
		self.value = None
		self.user = user


async def getID(user, session):
	ResolveVanity = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={STEAM}&vanityurl={user}"
	async with session.get(ResolveVanity) as response:
		userID = await response.json()
	if userID["response"]["success"] == 1:
		return userID["response"]["steamid"]
	return user


async def mainPage(user, session):
	userID = await getID(user, session)

	PlayerSummaries = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM}&steamids={userID}"
	PlayerLevel = f"https://api.steampowered.com/IPlayerService/GetSteamLevel/v1/?key={STEAM}&steamid={userID}"

	async with session.get(PlayerSummaries) as response:
		userInfo = await response.json()

	async with session.get(PlayerLevel) as response:
		userLevel = await response.json()

	userInfo = userInfo["response"]["players"][0]
	embed = discord.Embed(
		description=f"`{userInfo['profileurl'].split('/')[4]}` is level `{userLevel['response']['player_level']}`")
	embed.add_field(name="Member since", value=f"<t:{userInfo['timecreated']}:R>")
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
			name="Currently gaming", value=f"[{userInfo['gameextrainfo']}](https://store.steampowered.com/app/{userInfo['gameid']})", inline=False)
		embed.set_image(
			url=f"https://cdn.cloudflare.steamstatic.com/steam/apps/{userInfo['gameid']}/header.jpg")

	embed.title = userInfo["personaname"]
	embed.url = userInfo["profileurl"]
	embed.color = statuscolor
	embed.set_thumbnail(url=userInfo["avatarfull"])
	return embed


class Steam(commands.Cog):

	def __init__(self, bot):
		super().__init__()
		self.bot = bot

	@app_commands.command(name="steam", description="View steam profiles :)")
	@app_commands.describe(user="The user's vanity, steam id or discord mention if they linked their account",
						   ephemeral="Whether the result will be visible to you (True) or everyone else (False)")
	async def steam(self, interaction, user: str = None, ephemeral: bool = False):
		global STEAM
		STEAM = self.bot.config["keys"]["STEAM"]
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
				async with self.bot.db_pool.acquire() as conn:
					async with conn.transaction():
						socials = await conn.fetchval("SELECT socials FROM profiles WHERE id = $1", user_id)
						socials_dict = json.loads(socials)
						if 'steam' in socials_dict:
							user = socials_dict['steam']
						else:
							raise Exception

			except Exception as e:
				await interaction.response.send_message(f"{g} linked a `Steam` account! Run </link:1080264642569441380> to do so", ephemeral=True)
				return

		try:
			embed = await mainPage(user, self.bot.web_client)
			await interaction.response.send_message(embed=embed, ephemeral=ephemeral)

		except Exception as e:
			await interaction.response.send_message(f"I couldn't find the user. Did you use the vanity url of the user?", ephemeral=True)


async def setup(bot):
	await bot.add_cog(Steam(bot))
