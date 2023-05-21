from typing import Optional
import aiosqlite
import discord

from discord import ui
from discord.ext import commands
from discord import app_commands
from discord.utils import MISSING

from data import Data, DATABASE_FILE, icons

async def load_server(table: str, server_id: str, columns: list = None) -> Optional[dict]:
	"""Get a dict of the contents of selected columns in a database's row
	Args:
		table (str): The name of the db table
		server_id (str): The column to search from
		columns (list): A list of column names to fetch
	Returns:
		Optional[dict]: A dictionary of the contents of the selected columns of that row
	"""
	async with aiosqlite.connect(DATABASE_FILE) as conn:
		if columns is None or columns == []:
			query_columns = "*"
		else:
			query_columns = f"{', '.join(columns)}"
		async with conn.execute(f"SELECT {query_columns} FROM {table} WHERE server_id = ?", (server_id,)) as cursor:
			row = await cursor.fetchone()
			if row is None:
				await conn.execute(f"INSERT INTO {table} (server_id) VALUES (?)", (server_id,))
				await conn.commit()
				async with conn.execute(f"SELECT {query_columns} FROM {table} WHERE server_id = ?", (server_id,)) as cursor:
					row = await cursor.fetchone()
		if columns is None or columns == []:
			columns = [description[0]
					   for description in cursor.description]
		data = dict(zip(columns, row))
	return data

async def general_menu(settings):
	embed = discord.Embed()
	embed.title = "🔩 General"
	embed.add_field(name=f"Private: {str('`Hidden`' if settings['private'] else '`Shown`')}",
					value="Your tag won't be shown on leaderboards and other commands showing your user id / discriminator")
	embed.add_field(name=f"Levels: {str('`Enabled`' if settings['levels'] else '`Disabled`')}",
					value="Disabling levels will prevent you from gaining xp and leveling up")
	embed.set_footer(text="Select a value to toggle")
	return embed


async def main_menu(user, admin=False):
	embed = discord.Embed(title=str(user))
	embed.description = "Select an option to pick a category"
	embed.add_field(name="🔩 General",
					value="• Private\n• Levels", inline=True)
	embed.add_field(name="🎂 Social",
					value="• Birth year\n• Handles\n", inline=True)
	embed.add_field(name="🧰 Advanced",
					value="• Experiments\n• Reset data", inline=True)
	embed.set_footer(text="Select a value to toggle")
	if admin:
		embed.add_field(name="📂 Server",
					value="• Levels", inline=True)
	embed.set_thumbnail(url=user.display_avatar.url)
	return embed


async def social_menu(settings, user):
	embed = discord.Embed()
	embed.title = "🎂 Social"
	birthday = await Data.load_db(table="profiles", user_id=user.id, columns=["cake"])
	year_bool = birthday['cake'].split(":")[1]
	embed.add_field(name=f"Birth year: {str('`Shown`' if year_bool == 'True' else '`Hidden`')}",
					value="Hiding your birth year will not reveal your age in reminders"
					"and will hide it from your profile.\nRun </unlink:1080271956496101467> to remove your birthday")
	embed.add_field(name=f"Handles: {str('`Shown`' if settings['handles'] else '`Hidden`')}",
					value="Hiding handles will only allow you to run related commands with no arguments")
	embed.set_footer(text="Select a value to toggle")
	return embed

async def server_menu(icon, server_name, server):
	embed = discord.Embed()
	embed.title = "📂 Server"
	embed.description= f"Editing settings for `{server_name}`"
	embed.add_field(name=f"Levels: {str('`Enabled`' if server['levels'] else '`Disabled`')}",
					value="Disabling levels will prevent everyone in this server from gaining xp and leveling up")

	embed.set_thumbnail(url=icon)
	embed.set_footer(text="Select a value to toggle")
	return embed

async def advanced_menu(settings):
	embed = discord.Embed()
	embed.title = "🧰 Advanced"
	embed.add_field(name=f"Experiments: {str('`Enabled`' if settings['experiments'] else '`Disabled`')}",
					value="Experiments will give you access to broken, unfinished test features. Enable if you're fine with bugs!")
	embed.add_field(name="Reset data",
					value=":warning: *Cannot be undone!*\nDelete all your data including ranks, handles and everything we know about you.")
	embed.set_footer(text="Select a value to toggle")
	return embed


def colorize(value):
	if str(value) == "1":
		return discord.ButtonStyle.green
	return discord.ButtonStyle.gray


class ConfirmModal(ui.Modal):
	def __init__(self, *, title: str = "Are you sure?", timeout: float | None = 120) -> None:
		super().__init__(title=title, timeout=timeout)

	confirmation = discord.ui.TextInput(
		style=discord.TextStyle.short,
		label="This cannot be undone",
		required=False,
		max_length=500,
		placeholder="Type anything here and press submit to confirm."
	)

	async def on_submit(self, interaction: discord.Interaction):
		if not self.confirmation.value:
			await interaction.response.send_message(f"Alright, come back if you change your mind!", ephemeral=True)
			return
		await interaction.response.send_message(f"Wait while i delete everything i know about you...", ephemeral=True)
		await Data.commit_db(command=f"DELETE FROM rep WHERE user_id = ?", args=(interaction.user.id,))
		await Data.commit_db(command=f"DELETE FROM settings WHERE user_id = ?", args=(interaction.user.id,))
		followed_users = {'following': '[]'} or await Data.load_db("profiles", interaction.user.id, columns=["following"])

		for i in eval(followed_users['following']):
			print(i)
			userdata = await Data.load_db(table="profiles", user_id=i, columns=['follow_list'])
			print(userdata)
			follow_list = eval(userdata['follow_list'])
			follow_list = follow_list.remove(interaction.user.id)
			if follow_list is None:
				follow_list = []
			await Data.commit_db("UPDATE profiles SET follow_list=? WHERE user_id=?", (str(follow_list), i))
		await Data.commit_db(command=f"DELETE FROM profiles WHERE user_id=?", args=(interaction.user.id,))
		await interaction.followup.send("Everything is gone, bye-bye!", ephemeral=True)

class ServerMenu(ui.View):
	def __init__(self, data, admin):
		super().__init__()
		self.value = None
		self.admin = admin
		self.data = data

		for i in self.children:
			if not i.label or i.label == "Reset Data":
				continue
			i.style = colorize(
				self.data[i.label.lower()])
	
	@ui.button(label=None, emoji=icons["back"], style=discord.ButtonStyle.blurple)
	async def back(self, inter, button):
		view = SettingsMenu(inter.user, self.admin)
		embed = await main_menu(inter.user, admin=self.admin)

		await inter.response.edit_message(embed=embed, view=view)
		view.msg = await inter.original_response()
	
	@ui.button(label="Levels", style=discord.ButtonStyle.gray)
	async def lvl_button(self, inter, button):
		async with aiosqlite.connect(DATABASE_FILE) as db:
			value = 0
			if self.data['levels'] == 0:
				value = 1
			await db.execute(f"UPDATE servers SET levels=? WHERE server_id=?", (value, inter.guild.id))
			await db.commit()
		self.data = await load_server(table="servers", server_id=inter.guild.id)
		button.style = colorize(value=self.data['levels'])
		embed = await server_menu(inter.guild.icon.url, inter.guild.name, self.data)

		await inter.response.edit_message(embed=embed, view=self)

class AdvancedMenu(ui.View):
	def __init__(self, user, settings, admin):
		super().__init__()
		self.value = None
		self.user = user
		self.settings = settings
		self.admin = admin

		for i in self.children:
			if not i.label or i.label == "Reset Data":
				continue
			i.style = colorize(
				self.settings[i.label.lower()])

	@ui.button(label=None, emoji=icons["back"], style=discord.ButtonStyle.blurple)
	async def back(self, inter, button):
		view = SettingsMenu(inter.user, self.admin)
		embed = await main_menu(inter.user, admin=self.admin)

		await inter.response.edit_message(embed=embed, view=view)
		view.msg = await inter.original_response()

	@ui.button(label="Experiments", style=discord.ButtonStyle.gray)
	async def exp_button(self, inter, button):
		async with aiosqlite.connect(DATABASE_FILE) as db:
			value = 0
			if self.settings['experiments'] == 0:
				value = 1
			await db.execute(f"UPDATE settings SET experiments=? WHERE user_id=?", (value, self.user.id))
			await db.commit()
		self.settings = await Data.load_db(table="settings", user_id=self.user.id)
		button.style = colorize(value=self.settings['experiments'])
		embed = await advanced_menu(self.settings)

		await inter.response.edit_message(embed=embed, view=self)

	@ui.button(label="Reset Data", style=discord.ButtonStyle.red)
	async def reset_data(self, inter, button):
		modal = ConfirmModal()
		await inter.response.send_modal(modal)


class SocialMenu(ui.View):
	def __init__(self, user, settings, birthday, admin):
		super().__init__()
		self.value = None
		self.user = user
		self.settings = settings
		self.birthday = birthday
		self.admin = admin
		
		for i in self.children:
			if not i.label:
				continue

			if i.label.lower() == "birth year":
				i.style = colorize("0" if self.birthday.split(":")[
								   1] == "False" else "1")
				continue

			i.style = colorize(
				self.settings[i.label.lower()])

	@ui.button(label=None, emoji=icons["back"], style=discord.ButtonStyle.blurple)
	async def back(self, inter, button):
		view = SettingsMenu(inter.user, self.admin)
		embed = await main_menu(inter.user, admin=self.admin)

		await inter.response.edit_message(embed=embed, view=view)
		view.msg = await inter.original_response()

	@ui.button(label="Birth year", style=discord.ButtonStyle.gray)
	async def bday_button(self, inter, button):
		async with aiosqlite.connect(DATABASE_FILE) as db:
			date, year_bool = self.birthday.split(":")
			value = f"{date}:True"
			if year_bool == "True":
				year_bool = "False"
				value = f"{date}:False"
			await db.execute(f"UPDATE profiles SET cake=? WHERE user_id=?", (value, self.user.id))
			await db.commit()
		birthday = await Data.load_db(table="profiles", user_id=self.user.id, columns=['cake'])
		date, year_bool = self.birthday.split(":")
		year_bool = "0" if year_bool == "True" else "1"
		button.style = colorize(value=year_bool)
		self.birthday = birthday['cake']
		embed = await social_menu(self.settings, inter.user)

		await inter.response.edit_message(embed=embed, view=self)

	@ui.button(label="Handles", style=discord.ButtonStyle.gray)
	async def hndl_button(self, inter, button):
		async with aiosqlite.connect(DATABASE_FILE) as db:
			value = 0
			if self.settings['handles'] == 0:
				value = 1
			await db.execute(f"UPDATE settings SET handles=? WHERE user_id=?", (value, self.user.id))
			await db.commit()
		self.settings = await Data.load_db(table="settings", user_id=self.user.id)
		button.style = colorize(value=self.settings['handles'])
		embed = await social_menu(self.settings, inter.user)

		await inter.response.edit_message(embed=embed, view=self)


class GeneralMenu(ui.View):
	def __init__(self, user, settings, admin):
		super().__init__()
		self.value = None
		self.user = user
		self.settings = settings
		self.admin = admin

		for i in self.children:
			if i.label:
				i.style = colorize(
					self.settings[i.label.lower()])

	@ui.button(label=None, emoji=icons["back"], style=discord.ButtonStyle.blurple)
	async def back(self, inter, button):
		view = SettingsMenu(inter.user, self.admin)
		embed = await main_menu(inter.user, admin=self.admin)

		await inter.response.edit_message(embed=embed, view=view)
		view.msg = await inter.original_response()

	@ui.button(label="Private", style=discord.ButtonStyle.gray)
	async def vis_button(self, inter, button):
		async with aiosqlite.connect(DATABASE_FILE) as db:
			value = 0
			if self.settings['private'] == 0:
				value = 1
			await db.execute(f"UPDATE settings SET private=? WHERE user_id=?", (value, self.user.id))
			await db.commit()
		self.settings = await Data.load_db(table="settings", user_id=self.user.id)
		button.style = colorize(value=self.settings['private'])
		embed = await general_menu(self.settings)

		await inter.response.edit_message(embed=embed, view=self)

	@ui.button(label="Levels", style=discord.ButtonStyle.gray)
	async def lvl_button(self, inter, button):
		async with aiosqlite.connect(DATABASE_FILE) as db:
			value = 0
			if self.settings['levels'] == 0:
				value = 1
			await db.execute(f"UPDATE settings SET levels=? WHERE user_id=?", (value, self.user.id))
			await db.commit()
		self.settings = await Data.load_db(table="settings", user_id=self.user.id)
		button.style = colorize(value=self.settings['levels'])
		embed = await general_menu(self.settings)

		await inter.response.edit_message(embed=embed, view=self)


class SettingsMenu(ui.View):
	def __init__(self, user, admin):
		super().__init__()
		self.value = None
		self.user = user
		self.settings = None
		self.admin = admin
	
		for i in self.children:
			if i.label == "Server" and not self.admin:
				self.remove_item(i)

	async def interaction_check(self, interaction) -> bool:
		self.settings = await Data.load_db(table="settings", user_id=self.user.id)
		return True

	@ui.button(label="General", emoji="🔩", style=discord.ButtonStyle.blurple)
	async def general_button(self, inter, button):
		embed = await general_menu(self.settings)

		await inter.response.defer()
		await self.msg.edit(embed=embed, view=GeneralMenu(inter.user, self.settings, self.admin))

	@ui.button(label="Social", emoji="🎂", style=discord.ButtonStyle.blurple)
	async def social_button(self, inter, button):
		embed = await social_menu(self.settings, self.user)

		birthday = await Data.load_db(table="profiles", user_id=self.user.id)
		await inter.response.defer()
		await self.msg.edit(embed=embed, view=SocialMenu(inter.user, self.settings, birthday['cake'], self.admin))

	@ui.button(label="Advanced", emoji="🧰", style=discord.ButtonStyle.blurple)
	async def advanced_button(self, inter, button):
		embed = await advanced_menu(self.settings)

		await inter.response.defer()
		await self.msg.edit(embed=embed, view=AdvancedMenu(inter.user, self.settings, self.admin))
	
	@ui.button(label="Server", emoji="📂", style=discord.ButtonStyle.blurple, row=2)
	async def serv_button(self, inter, button):
		data = await load_server(table="servers", server_id=inter.guild.id)
		embed = await server_menu(icon=inter.guild.icon.url, server_name=inter.guild.name, server=data)

		await inter.response.defer()
		await self.msg.edit(embed=embed, view=ServerMenu(data, admin=self.admin))


class Settings(commands.Cog):
	def __init__(self, ce: commands.Bot):
		self.ce = ce

	@app_commands.command(name="settings", description="Tweak the bot's settings to your likings")
	async def settings(self, interaction):
		settings = await Data.load_db(table="settings", user_id=interaction.user.id)
		if not settings:
			async with aiosqlite.connect(DATABASE_FILE) as db:
				await db.execute(f"INSERT INTO settings (user_id) VALUES (?)", (interaction.user.id,))
				await db.commit()
			settings = await Data.load_db(table="settings", user_id=interaction.user.id)
		
		admin = True if interaction.guild and interaction.user.guild_permissions.administrator else False
		menu = SettingsMenu(interaction.user, admin)
		embed = await main_menu(interaction.user, admin=admin)
		embed.set_thumbnail(url=interaction.user.display_avatar.url)
		await interaction.response.send_message(embed=embed, view=menu, ephemeral=True)
		menu.msg = await interaction.original_response()


async def setup(ce: commands.Bot):
	await ce.add_cog(Settings(ce))
