import struct

import aiohttp
import discord
import toml
from discord import app_commands
from discord.ext import commands

class DownloadButton(discord.ui.View):

	def __init__(self):
		super().__init__()
		self.value = None

config = toml.load("config.toml")
token = config["TOKEN"]
app = token

icons = {"active_developer": "<:Active_Developer:1078093417680224356>", "bot_http_interactions": "<:Supports_Commands:1078022481144729620>",
		 "bug_hunter": "<:Bug_Hunter:1078015408684142743>", "bug_hunter_level_2": "<:Bug_Hunter_Level_2:1078015437285097542>",
		 "discord_certified_moderator": "<:Discord_Mod_Alumni:1078091018886451281>", "early_supporter": "<:Early_Supporter:1078015810909524149>",
		 "early_verified_bot_developer": "<:Verified_Bot_Developer:1078094815398461450>", "hypesquad": "<:HypeSquad_Event:1078014370912686180>",
		 "hypesquad_balance": "<:HypeSquad_Balance:1078014406396485642>", "hypesquad_bravery": "<:HypeSquad_Bravery:1078014366953242794>",
		 "hypesquad_brilliance": "<:HypeSquad_Brilliance:1078014368454820010>", "partner": "<:Discord_Partner:1078021591859986463>",
		 "staff": "<:Discord_Staff:1078015590683390093>", "verified_bot": "<:Verified_Bot:1078090782118002719> "}

def stamp(snowflake_id):
	snowflake_struct = struct.unpack(
		'>Q', snowflake_id.to_bytes(8, byteorder='big'))[0]
	timestamp = (snowflake_struct >> 22) + 1420070400000
	return int(timestamp / 1000)


statuscodes = [
	'100', '101', '102', '200', '201', '202', '203', '204', '206', '207', '300', '301', '302', '303', '304', '305',
	'307', '308', '400', '401', '402', '403', '404', '405', '406', '407', '408', '409', '410', '411', '412', '413',
	'414', '415', '416', '417', '418', '420', '422', '423', '424', '425', '426', '429', '431', '444', '450', '451',
	'497', '498', '499', '500', '501', '502', '503', '504', '506', '507', '508', '509', '510', '511', '521', '522',
	'523', '525', '599']


class DiscordID(commands.Cog):
	def __init__(self, ce) -> None:
		super().__init__()
		self.ce = ce

	@app_commands.command(name="profile", description="View anyone's profile from their id")
	async def discord_id(self, interaction, userid: str = None):
		userid = userid or interaction.user.id
		if userid.startswith("<@"):
			userid = int(userid[2:-1])
		
		if not type(userid) == int:
			await interaction.response.send_message("The id is not valid")
			return

		user = await self.ce.fetch_user(userid)
		url = f"https://discord.com/api/v9/users/{userid}"
		headers = {"Authorization": f"Bot {app}"}

		async with aiohttp.ClientSession() as session:
			response = await session.get(url, headers=headers)
			if response.status != 200:
				await interaction.response.send_message(f"https://http.cat/{response.status_code}.jpg",
													ephemeral=True)
				return
			try:
				data = await response.json()
				embed = discord.Embed(
					title=f"{data['username']}#{data['discriminator']}",
					url=f"https://discord.com/users/{userid}")
				ext = "png"
				if data["avatar"].startswith("a_"):
					ext = "gif"
				embed.set_thumbnail(
					url=f"https://cdn.discordapp.com/avatars/{userid}/{data['avatar']}.{ext}?size=4096")
				if data["accent_color"] is not None:
					embed.color = data["accent_color"]
				if data["banner"] is not None:
					ext = "png"
					if data["banner"].startswith("a_"):
						ext = "gif"
					embed.set_image(
						url=f"https://cdn.discordapp.com/banners/{userid}/{data['banner']}.{ext}?size=4096")
				embed.add_field(name="Public flags",
								value=data["public_flags"])
				embed.add_field(name="Creation date",
								value=f"<t:{stamp(int(userid))}:R>")
				badges_list = []
				for flag in user.public_flags.all():
					badges_list.append(icons[flag.name])
				if data["avatar"].startswith("a_") or data["banner"] is not None:
					badges_list.append("<:nitro:1078094211351584928>")
				if user.bot:
					badges_list.append("<:bot:1078091845051088979>")

				if user.id in config["contributors"]:
					badges_list.append("<:Contributor:1078661797185335398>")

				if user.id in config["special"]:
					badges_list.append("<:Special:1078664371661713449>")
				#if user.id == 912091795318517821:
				#	badges_list = []
				#	for icon in icons:
				#		badges_list.append(icons[icon])
				#	badges_list.append("<:nitro:1078094211351584928>")
				#	badges_list.append("<:bot:1078091845051088979>")

				result = ' '.join(badges_list)
				embed.description = result

				view = DownloadButton()
				view.add_item(discord.ui.Button(label='Avatar', style=discord.ButtonStyle.link, url=f"https://cdn.discordapp.com/avatars/{userid}/{data['avatar']}.{ext}?size=4096",
										emoji='<:download:1062784992243105813>'))
				if data["banner"] is not None:
					view.add_item(discord.ui.Button(label='Banner', style=discord.ButtonStyle.link, url=f"https://cdn.discordapp.com/banners/{userid}/{data['banner']}.{ext}?size=4096",
											emoji='<:download:1062784992243105813>'))
				await interaction.response.send_message(embed=embed, view=view)
			except Exception as e:
				await interaction.response.send_message(e)


async def setup(ce):
	await ce.add_cog(DiscordID(ce))
