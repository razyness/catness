import struct

import aiohttp
import discord
import aiosqlite
import calendar
import json

from datetime import datetime
from discord import app_commands
from discord.ext import commands

from data import config, Data, icons, DATABASE_FILE
from utils.http import HTTP


class DownloadButton(discord.ui.View):

	def __init__(self):
		super().__init__()
		self.value = None


class RemoveView(discord.ui.View):
	def __init__(self, user, author):
		super().__init__()
		self.value = None
		self.user = user
		self.author = author

	async def remove_birthday(self, user, author):
		try:
			async with aiosqlite.connect(DATABASE_FILE) as conn:
				async with conn.execute("SELECT follow_list FROM profiles WHERE user_id=?", (user,)) as cursor:
					row = await cursor.fetchone()
					if row is not None:
						follow_list_str = row[0]
						follow_list = []
						if follow_list_str:
							follow_list = json.loads(follow_list_str)
						if author in follow_list:
							follow_list.remove(author)
							follow_list_str = json.dumps(follow_list)
							await conn.execute("UPDATE profiles SET follow_list=? WHERE user_id=?", (follow_list_str, user))
							await conn.commit()
							return {"user_id": user, "follow_list": follow_list}

		except Exception as e:
			print(e)



	@discord.ui.button(label="Cancel", emoji=icons["remove"], style=discord.ButtonStyle.red)
	async def remove_cake(self, inter, button):
		try:
			await self.remove_birthday(self.user.id, self.author.id)
			await inter.response.send_message(f"You will not be notified on {self.user.mention}'s birthday", ephemeral=True)
		except Exception as e:
			await inter.response.send_message(e, ephemeral=True)


class ProfileView(discord.ui.View):

	def __init__(self, user):
		super().__init__()
		self.value = None
		self.user = user

	async def disable_all(self):
		for i in self.children:
			i.disabled = True
		await self.msg.edit(view=self)

	async def on_timeout(self):
		await self.disable_all()

	async def notify_action(self, user):
		try:
			async with aiosqlite.connect(DATABASE_FILE) as conn:
				async with conn.execute("SELECT follow_list FROM profiles WHERE user_id=?", (self.user.id,)) as cursor:
					row = await cursor.fetchone()
					follow_list = []
					if row is not None:
						follow_list_str = row[0]
						if follow_list_str:
							follow_list = follow_list_str.strip("[]").split(',')
							follow_list = [int(user_id) for user_id in follow_list]
					if user.id not in follow_list:
						follow_list.append(user.id)
						follow_list_str = str(follow_list)
						if row is not None:
							await conn.execute("UPDATE profiles SET follow_list=? WHERE user_id=?", (follow_list_str, self.user.id))
						else:
							await conn.execute("INSERT INTO profiles (user_id, follow_list) VALUES (?, ?)", (self.user.id, follow_list_str))
						await conn.commit()

			return f"You are now following {self.user.mention}'s birthday!"
		except:
			return f"You are already following {self.user.mention}'s birthday!"

	@discord.ui.button(label="Notify me!", emoji="🎂", style=discord.ButtonStyle.blurple)
	async def notify(self, inter, button):
		resp = await self.notify_action(inter.user)
		view = RemoveView(self.user, inter.user)
		await inter.response.send_message(resp, view=view, ephemeral=True)

	async def interaction_check(self, interaction) -> bool:
		if interaction.user.id == self.user.id:
			await interaction.response.send_message("You can't follow your own birthday, you should remember it i think", ephemeral=True)
			return False
		return True


token = config["TOKEN"]
app = token


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
	@app_commands.describe(user="Hello pick a user or leave empty for yourself")
	async def discord_id(self, interaction, user: str = None):
		if user is None:
			user = interaction.user.id
		elif user.startswith("<@"):
			user = int(user[2:-1])
		else:
			try:
				user = int(user)
			except:
				await interaction.response.send_message("The id is not valid", ephemeral=True)
				return

		real_user = await self.ce.fetch_user(user)
		url = f"https://discord.com/api/v9/users/{user}"
		headers = {"Authorization": f"Bot {app}"}

		async with aiohttp.ClientSession() as session:
			response = await session.get(url, headers=headers)
			if response.status != 200:
				await interaction.response.send_message(f"https://http.cat/{response.status_code}.jpg",
														ephemeral=True)
				return
			data = await response.json()
			embed = discord.Embed(
				title=f"{data['username']}#{data['discriminator']}",
				url=f"https://discord.com/users/{user}")
			ext = "png"
			if data["avatar"].startswith("a_"):
				ext = "gif"
			embed.set_thumbnail(
				url=f"https://cdn.discordapp.com/avatars/{user}/{data['avatar']}.{ext}?size=4096")
			if data["accent_color"] is not None:
				embed.color = data["accent_color"]
			if data["banner"] is not None:
				ext = "png"
				if data["banner"].startswith("a_"):
					ext = "gif"
				embed.set_image(
					url=f"https://cdn.discordapp.com/banners/{user}/{data['banner']}.{ext}?size=4096")
			embed.add_field(name="Public flags",
							value=data["public_flags"])
			embed.add_field(name="Creation date",
							value=f"<t:{stamp(int(user))}:R>")
			badges_list = []
			for flag in real_user.public_flags.all():
				badges_list.append(icons[flag.name])
			if data["avatar"].startswith("a_") or data["banner"] is not None:
				badges_list.append("<:nitro:1078094211351584928>")
			if real_user.bot:
				badges_list.append("<:bot:1078091845051088979>")
			if real_user.id in config["contributors"]:
				badges_list.append("<:Contributor:1078661797185335398>")
			if real_user.id in config["special"]:
				badges_list.append("<:Special:1078664371661713449>")
				
			#if user == 912091795318517821:
			#    badges_list = []
			#for icon in icons:
			#    badges_list.append(icons[icon])
			#badges_list.append("<:nitro:1078094211351584928>")
			#badges_list.append("<:bot:1078091845051088979>")
				
			result = ' '.join(badges_list)
			embed.description = result
			view = DownloadButton()
			profiles = []

			async with aiosqlite.connect('data/data.db') as db:
				db.row_factory = aiosqlite.Row
				cursor = await db.execute("SELECT * FROM profiles WHERE user_id = ?", (user,))
				social_data = await cursor.fetchone()

			if social_data:
				for handle_type in ['lastfm', 'steam']:
					handle_value = social_data[handle_type]
					if handle_value is not None:
						profiles.append(
							f"{icons[handle_type]} `{handle_value}`")
				result = '\n'.join(profiles)

				if profiles != []:
					embed.add_field(name="Linked profiles",
									value=result, inline=True)

				date_str = social_data['cake']
				if date_str is not None:
					date, consider_age = date_str.split(':')
					if consider_age == "True":
						formatted_date = f"<t:{int(datetime.strptime(date, '%d/%m/%Y').timestamp())}:D>"
					else:
						day, month, year = date.split("/")
						month = calendar.month_name[int(month)]
						formatted_date = f"`{day} {month}`"
					view = ProfileView(user=await self.ce.fetch_user(user))
					embed.add_field(name="Birthday", value=formatted_date)

			ruser = await Data.load_db(table="rep", value=user)

			if ruser is None:
				rep = 0
			else:
				rep = ruser["rep"]

			embed.add_field(name="Rep nepnep",
							value=f"`{rep}` points", inline=True)

			view.add_item(discord.ui.Button(label='Avatar', style=discord.ButtonStyle.link, url=f"https://cdn.discordapp.com/avatars/{user}/{data['avatar']}.{ext}?size=4096",
											emoji='<:download:1062784992243105813>'))
			if data["banner"] is not None:
				view.add_item(discord.ui.Button(label='Banner', style=discord.ButtonStyle.link, url=f"https://cdn.discordapp.com/banners/{user}/{data['banner']}.{ext}?size=4096",
												emoji='<:download:1062784992243105813>'))

			await interaction.response.send_message(embed=embed, view=view)
			view.msg = await interaction.original_response()


async def setup(ce):
	await ce.add_cog(DiscordID(ce))
