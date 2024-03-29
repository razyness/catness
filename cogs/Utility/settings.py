from typing import Optional
import discord
import json
from discord import ui
from discord.ext import commands
from discord import app_commands
from discord.utils import MISSING

from utils import icons
from utils import blocking
from utils import confirm

labels = {
	'pomelo': 'profile_private',
	'levels': 'levels_enabled',
	'experiments': 'tests_enabled',
	'welcomer': 'welcome_type'

}


async def load_db(db_pool, id, table):
	async with db_pool.acquire() as conn:
		row = await conn.fetchrow(f"SELECT * FROM {table} WHERE id=$1", id)
		if row:
			result = dict(row)
			return result
		return None


async def general_menu(settings):
	embed = discord.Embed()
	embed.title = "🔩 General"
	embed.add_field(name=f"Pomelo: {str('`Hidden`' if settings['profile_private'] else '`Shown`')}",
					value="Your tag/pomelo won't be shown on leaderboards and other commands, instead using your display name")
	embed.add_field(name=f"Levels: {str('`Enabled`' if settings['levels_enabled'] else '`Disabled`')}",
					value="Disabling levels will prevent you from gaining xp and leveling up")
	embed.set_footer(text="Select a value to toggle")
	return embed


async def main_menu(user, admin=False):
	embed = discord.Embed(title=str(user))
	embed.description = "Select an option to pick a category"
	embed.add_field(name="🔩 General",
					value="• Pomelo\n• Levels", inline=True)
	embed.add_field(name="🎂 Social",
					value="• Birth year", inline=True)
	embed.add_field(name="🧰 Advanced",
					value="• Experiments\n• Reset data", inline=True)
	embed.set_footer(text="Select a value to toggle")
	if admin:
		embed.add_field(name="📂 Server",
						value="• Levels\n• Welcomer\n• Features", inline=True)
	embed.set_thumbnail(url=user.display_avatar.url)
	return embed


async def social_menu(settings, *args):
	embed = discord.Embed()
	embed.title = "🎂 Social"
	birthday = None
	year_bool = None
	if settings['cake']:
		birthday = await blocking.run(lambda: json.loads(settings['cake']))

	warn = None

	if birthday:
		year_bool = True if birthday['consider'] else False
	else:
		warn = "⚠️ `Your birthday is not set`\n"

	embed.add_field(name=f"Birth year: {str('`Shown`' if year_bool else '`Hidden`')}",
					value=f"{warn}Hiding your birth year will not reveal your age in reminders"
						  "and your profile.\nRun </unlink:1080271956496101467> to remove your birthday")
	embed.set_footer(text="Select a value to toggle")
	return embed


async def server_menu(icon, server_name, server, server_obj):
	if icon:
		icon = icon.url

	patterns = ["general", "main", "chat"]
	welc_channel = next((channel for channel in server_obj.text_channels if any(
		name.lower() in channel.name.lower() for name in patterns)), None)
	welc_channel = "`None`" if not welc_channel else f"<#{welc_channel.id}>"
	embed = discord.Embed()
	embed.title = "📂 Server"
	embed.description = f"Editing settings for `{server_name}`"
	embed.add_field(name=f"Levels: {str('`Enabled`' if server['levels_enabled'] else '`Disabled`')}",
					value="Disabling levels will prevent everyone in this server from gaining xp and leveling up")
	embed.add_field(
		name=f"Welcomer: {str('`Disabled`' if server['welcome_type'] == 0 else '`Enabled`' if server['welcome_type'] == 1 else '`Enabled - Prompt`')}",
		value=f"Greets new members with a random message.\nWelcome channel: {welc_channel}")
	embed.add_field(name=f"Features: {str('`Enabled`' if server['features'] else '`Disabled`')}",
					value="Enables on message features such as /#color previews, booster hearts, etc. for this server")
	embed.set_thumbnail(url=icon)
	embed.set_footer(text="Select a value to toggle")
	return embed


async def advanced_menu(settings):
	embed = discord.Embed()
	embed.title = "🧰 Advanced"
	embed.add_field(name=f"Experiments: {str('`Enabled`' if settings['tests_enabled'] else '`Disabled`')}",
					value="Experiments will give you access to broken, unfinished test features. Enable if you're fine with bugs!")
	embed.add_field(name="Reset data",
					value=":warning: *Cannot be undone!*\nDelete all your data including ranks, handles and everything we know about you.")
	embed.set_footer(text="Select a value to toggle")
	return embed


def colorize(value):
	if int(value) >= 1:
		return discord.ButtonStyle.green
	return discord.ButtonStyle.gray


class ServerMenu(ui.View):
	def __init__(self, data, admin, db_pool):
		super().__init__()
		self.value = None
		self.admin = admin
		self.data = data
		self.db_pool = db_pool

		for i in self.children:
			if i.label and i.label not in ["Reset Data"]:
				replacement = labels.get(i.label.lower(), i.label.lower())
				i.style = colorize(self.data[replacement])

	@ui.button(label=None, emoji=icons["back"], style=discord.ButtonStyle.blurple)
	async def back(self, inter, button):
		view = SettingsMenu(inter.user, self.admin, self.db_pool)
		embed = await main_menu(inter.user, admin=self.admin)

		await inter.response.edit_message(embed=embed, view=view)
		view.msg = await inter.original_response()

	@ui.button(label="Levels", style=discord.ButtonStyle.gray)
	async def lvl_button(self, inter, button):
		async with self.db_pool.acquire() as conn:
			value = False
			if not self.data['levels_enabled']:
				value = True
			await conn.execute(f"UPDATE servers SET levels_enabled=$1 WHERE id=$2", value, inter.guild.id)
		self.data = await load_db(db_pool=self.db_pool, table="servers", id=inter.guild.id)
		button.style = colorize(value=self.data['levels_enabled'])
		embed = await server_menu(inter.guild.icon, inter.guild.name, self.data, inter.guild)

		await inter.response.edit_message(embed=embed, view=self)

	@ui.button(label="Welcomer", style=discord.ButtonStyle.gray)
	async def welc_button(self, inter, button):
		async with self.db_pool.acquire() as conn:
			value = 0
			if self.data['welcome_type'] == 0:
				value = 1
			elif self.data['welcome_type'] == 1:
				value = 2

			await conn.execute(f"UPDATE servers SET welcome_type=$1 WHERE id=$2", value, inter.guild.id)
		self.data = await load_db(db_pool=self.db_pool, table="servers", id=inter.guild.id)
		button.style = colorize(value=self.data['welcome_type'])
		embed = await server_menu(inter.guild.icon, inter.guild.name, self.data, inter.guild)

		await inter.response.edit_message(embed=embed, view=self)

	@ui.button(label="Features", style=discord.ButtonStyle.gray)
	async def feat_button(self, inter, button):
		async with self.db_pool.acquire() as conn:
			value = False
			if not self.data['features']:
				value = True
			await conn.execute(f"UPDATE servers SET features=$1 WHERE id=$2", value, inter.guild.id)
		self.data = await load_db(db_pool=self.db_pool, table="servers", id=inter.guild.id)
		button.style = colorize(value=self.data['features'])
		embed = await server_menu(inter.guild.icon, inter.guild.name, self.data, inter.guild)

		await inter.response.edit_message(embed=embed, view=self)


class AdvancedMenu(ui.View):
	def __init__(self, user, settings, admin, db_pool):
		super().__init__()
		self.value = None
		self.user = user
		self.settings = settings
		self.admin = admin
		self.db_pool = db_pool

		for i in self.children:
			if i.label and i.label not in ["Reset Data"]:
				replacement = labels.get(i.label.lower(), i.label.lower())
				i.style = colorize(self.settings[replacement])

	@ui.button(label=None, emoji=icons["back"], style=discord.ButtonStyle.blurple)
	async def back(self, inter, button):
		view = SettingsMenu(inter.user, self.admin, self.db_pool)
		embed = await main_menu(inter.user, admin=self.admin)

		await inter.response.edit_message(embed=embed, view=view)
		view.msg = await inter.original_response()

	@ui.button(label="Experiments", style=discord.ButtonStyle.gray)
	async def exp_button(self, inter, button):
		async with self.db_pool.acquire() as conn:
			value = False
			if self.settings['tests_enabled'] == False:
				value = True
			await conn.execute(f"UPDATE profiles SET tests_enabled=$1 WHERE id=$2", value, self.user.id)
		self.settings = await load_db(db_pool=self.db_pool, table="profiles", id=self.user.id)
		button.style = colorize(value=self.settings['tests_enabled'])
		embed = await advanced_menu(self.settings)

		await inter.response.edit_message(embed=embed, view=self)

	@ui.button(label="Reset Data", style=discord.ButtonStyle.red)
	async def reset_data(self, inter, button):
		conf = await confirm.send(inter, "Do you want to be forgotten?", "This cannot be undone")
		if not conf:
			await inter.followup.send("Alright, come back if you change your mind!", ephemeral=True)
			return

		await inter.followup.send(f"Wait while i delete everything i know about you...", ephemeral=True)
		async with self.db_pool.acquire() as conn:
			follows = await load_db(db_pool=self.db_pool, table="profiles", id=inter.user.id)
			follows = await blocking.run(lambda: json.loads(follows['follows']))

			for i in follows['following']:
				i = int(i)

				userdata = await load_db(db_pool=self.db_pool, table="profiles", id=i)

				follow_list = await blocking.run(lambda: json.loads(userdata['follows']))
				follow_list['followers'].remove(inter.user.id)
				follow_list = await blocking.run(lambda: json.dumps(follow_list))
				await conn.execute("UPDATE profiles SET follows=$1 WHERE id=$2", follow_list, i)

			for i in follows['followers']:
				i = int(i)

				userdata = await load_db(db_pool=self.db_pool, table="profiles", id=i)

				follow_list = await blocking.run(lambda: json.loads(userdata['follows']))
				follow_list['following'].remove(inter.user.id)
				follow_list = await blocking.run(lambda: json.dumps(follow_list))
				await conn.execute("UPDATE profiles SET follows=$1 WHERE id=$2", follow_list, i)

			await conn.execute("DELETE FROM profiles WHERE id=$1", inter.user.id)
		await inter.followup.send("Everything is gone, bye-bye!", ephemeral=True)


class SocialMenu(ui.View):
	def __init__(self, user, settings, birthday, admin, db_pool):
		super().__init__()
		self.value = None
		self.user = user
		self.settings = settings
		self.birthday = birthday
		self.admin = admin
		self.db_pool = db_pool

		for i in self.children:
			if not i.label:
				continue

			if i.label.lower() == "birth year":
				if self.birthday is None:
					i.style = discord.ButtonStyle.gray
					i.disabled = True
					continue
				i.style = colorize(
					"0" if not self.birthday['consider'] else "1")
				continue

			i.style = colorize(
				self.settings[i.label.lower()])

	@ui.button(label=None, emoji=icons["back"], style=discord.ButtonStyle.blurple)
	async def back(self, inter, button):
		view = SettingsMenu(inter.user, self.admin, self.db_pool)
		embed = await main_menu(inter.user, admin=self.admin)

		await inter.response.edit_message(embed=embed, view=view)
		view.msg = await inter.original_response()

	@ui.button(label="Birth year", style=discord.ButtonStyle.gray)
	async def bday_button(self, inter, button):
		async with self.db_pool.acquire() as conn:
			if self.birthday['consider']:
				self.birthday['consider'] = False
			else:
				self.birthday['consider'] = True

			cake = await blocking.run(lambda: json.dumps(self.birthday))
			await conn.execute(f"UPDATE profiles SET cake=$1 WHERE id=$2", cake, self.user.id)

		self.settings['cake'] = cake

		year_bool = "1" if self.birthday['consider'] else "0"
		button.style = colorize(value=year_bool)
		embed = await social_menu(self.settings, inter.user)

		await inter.response.edit_message(embed=embed, view=self)


class GeneralMenu(ui.View):
	def __init__(self, user, settings, admin, db_pool):
		super().__init__()
		self.value = None
		self.user = user
		self.settings = settings
		self.admin = admin
		self.db_pool = db_pool

		for i in self.children:
			if i.label:
				replacement = labels.get(i.label.lower(), i.label.lower())
				i.style = colorize(self.settings[replacement])

	@ui.button(label=None, emoji=icons["back"], style=discord.ButtonStyle.blurple)
	async def back(self, inter, button):
		view = SettingsMenu(inter.user, self.admin, self.db_pool)
		embed = await main_menu(inter.user, admin=self.admin)

		await inter.response.edit_message(embed=embed, view=view)
		view.msg = await inter.original_response()

	@ui.button(label="Pomelo", style=discord.ButtonStyle.gray)
	async def vis_button(self, inter, button):
		async with self.db_pool.acquire() as conn:
			value = False
			if self.settings['profile_private'] == False:
				value = True
			await conn.execute(f"UPDATE profiles SET profile_private=$1 WHERE id=$2", value, self.user.id)
		self.settings = await load_db(db_pool=self.db_pool, table="profiles", id=self.user.id)
		button.style = colorize(value=self.settings['profile_private'])
		embed = await general_menu(self.settings)

		await inter.response.edit_message(embed=embed, view=self)

	@ui.button(label="Levels", style=discord.ButtonStyle.gray)
	async def lvl_button(self, inter, button):
		async with self.db_pool.acquire() as conn:
			value = False
			if self.settings['levels_enabled'] == False:
				value = True
			await conn.execute(f"UPDATE profiles SET levels_enabled=$1 WHERE id=$2", value, self.user.id)
		self.settings = await load_db(db_pool=self.db_pool, table="profiles", id=self.user.id)
		button.style = colorize(value=self.settings['levels_enabled'])
		embed = await general_menu(self.settings)

		await inter.response.edit_message(embed=embed, view=self)


class SettingsMenu(ui.View):
	def __init__(self, user, admin, db_pool):
		super().__init__()
		self.value = None
		self.user = user
		self.settings = None
		self.admin = admin
		self.db_pool = db_pool

		for i in self.children:
			if i.label == "Server" and not self.admin:
				self.remove_item(i)

	async def interaction_check(self, interaction) -> bool:
		self.settings = await load_db(db_pool=self.db_pool, table="profiles", id=self.user.id)
		return True

	@ui.button(label="General", emoji="🔩", style=discord.ButtonStyle.blurple)
	async def general_button(self, inter, button):
		embed = await general_menu(self.settings)

		await inter.response.defer()
		await self.msg.edit(embed=embed, view=GeneralMenu(inter.user, self.settings, self.admin, self.db_pool))

	@ui.button(label="Social", emoji="🎂", style=discord.ButtonStyle.blurple)
	async def social_button(self, inter, button):
		embed = await social_menu(self.settings, self.user)
		cake = None
		self.settings = await load_db(db_pool=self.db_pool, table="profiles", id=self.user.id)
		if self.settings['cake']:
			cake = await blocking.run(lambda: json.loads(self.settings['cake']))
		await inter.response.defer()
		await self.msg.edit(embed=embed, view=SocialMenu(inter.user, self.settings, cake, self.admin, self.db_pool))

	@ui.button(label="Advanced", emoji="🧰", style=discord.ButtonStyle.blurple)
	async def advanced_button(self, inter, button):
		embed = await advanced_menu(self.settings)

		await inter.response.defer()
		await self.msg.edit(embed=embed, view=AdvancedMenu(inter.user, self.settings, self.admin, self.db_pool))

	@ui.button(label="Server", emoji="📂", style=discord.ButtonStyle.blurple, row=2)
	async def serv_button(self, inter, button):
		data = await load_db(db_pool=self.db_pool, table="servers", id=inter.guild.id)
		embed = await server_menu(icon=inter.guild.icon, server_name=inter.guild.name, server=data,
								  server_obj=inter.guild)

		await inter.response.defer()
		await self.msg.edit(embed=embed, view=ServerMenu(data, self.admin, self.db_pool))


class Settings(commands.Cog):
	"""A cog for managing user settings, such as privacy, levels, etc. Chat interface.
	"""

	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(name="settings", description="Tweak the bot's settings to your likings")
	async def settings(self, interaction):
		async with self.bot.db_pool.acquire() as conn:
			async with conn.transaction():
				settings = await conn.fetchrow("SELECT * FROM profiles WHERE id=$1", interaction.user.id)
				if not settings:
					await conn.execute("INSERT INTO profiles (id) VALUES ($1)", interaction.user.id)
					settings = await conn.fetchrow("SELECT * FROM profiles WHERE id=$1", interaction.user.id)

		def has_permissions(r): return (
				r.guild_permissions.administrator or
				r.guild_permissions.manage_roles or
				r.guild_permissions.manage_channels or
				r.guild_permissions.manage_messages or
				r.guild_permissions.ban_members or
				r.guild_permissions.kick_members
		)

		admin = True if interaction.guild and (
					interaction.user.guild_permissions.administrator or has_permissions(interaction.user)) else False
		menu = SettingsMenu(interaction.user, admin, db_pool=self.bot.db_pool)
		embed = await main_menu(interaction.user, admin=admin)
		embed.set_thumbnail(url=interaction.user.display_avatar.url)
		await interaction.response.send_message(embed=embed, view=menu, ephemeral=True)
		menu.msg = await interaction.original_response()


async def setup(bot: commands.Bot):
	await bot.add_cog(Settings(bot))
