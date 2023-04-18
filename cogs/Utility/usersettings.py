import sqlite3
import aiosqlite
import discord

from discord import ui
from discord.ext import commands
from discord import app_commands

from data import Data, DATABASE_FILE

class SelectMenu(ui.Select):
	def __init__(self, user):
		self.menu = SettingsMenu(user)
		options = [
			discord.SelectOption(label="Main page", value="main", emoji="🏠"),
			discord.SelectOption(label="General", value="general", emoji="⚙️"),
			discord.SelectOption(label="Social", value="social", emoji="🎂"),
			discord.SelectOption(label="Advanced", value="advanced", emoji="🧰"),
		]
		self.default = "main"
		self.user = user

		super().__init__(placeholder="Choose a category:",
						 min_values=1, max_values=1, options=options)

	async def callback(self, interaction: discord.Interaction):
		embed = None
		if self.values[0] == "Main page":
			embed = self.menu.main_menu()
		elif self.values[0] == "General":
			embed = self.menu.general_menu()
		await interaction.edit_original_response(embed=embed)


class SelectView(discord.ui.View):
	def __init__(self, user, *, timeout=180):
		super().__init__(timeout=timeout)
		self.add_item(SelectMenu(user))


class SettingsMenu(ui.View):
	def __init__(self, user):
		super().__init__()
		self.value = None
		self.user = user
		self.settings = None

	async def reload_db(self, user):
		async with aiosqlite.connect(DATABASE_FILE) as db:
			db.row_factory = aiosqlite.Row
			cursor = await db.execute("SELECT * FROM settings WHERE user_id = ?", (user.id,))
			self.settings = await cursor.fetchone()
			if self.settings is None:
				await db.execute(f"INSERT INTO settings (user_id) VALUES ('{user.id}')")
				await db.commit()
				self.settings = await cursor.fetchone()
			return self.settings

	async def align_values(self, string):
		lines = string.split('\n')
		for i, line in enumerate(lines):
			parts = line.split(':')
			if len(parts) == 2:
				key = parts[0].strip()
				value = parts[1].strip()
				lines[i] = f"{key:<20}{value:>10}"
		return '\n'.join(lines)

	async def general_menu(self):
		embed = discord.Embed()
		embed.title = "⚙ General"

		settings = await self.reload_db(self.user)
		string = ""
		print(settings)
		for key in settings:
			if key != 'user_id':
				value = settings[key]
				string = f"{string}\n{key}: {value.replace((0, 1), ('`OFF`', '`ON`'))}"

		embed.description = await self.align_values(string)
		embed.set_footer(text="Select a value to toggle")
		return embed

	async def main_menu(self):
		embed = discord.Embed(title=str(self.user))
		embed.description = "Select an option to pick a category"
		embed.add_field(name="⚙ General",
						value="• Visibility\n• Levels", inline=True)
		embed.add_field(name="🎂 Social",
						value="• Birthday\n• Handles\n", inline=True)
		embed.add_field(name="🧰 Advanced", value="• Experiments", inline=True)
		return embed


class Settings(commands.Cog):
	def __init__(self, ce: commands.Bot):
		self.ce = ce

	@app_commands.command(name="settings", description="Tweak the bot's settings to your likings")
	async def settings(self, interaction):
		menu = SettingsMenu(interaction.user)
		embed = await menu.main_menu()
		view = SelectView(interaction.user)
		await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(ce: commands.Bot):
	await ce.add_cog(Settings(ce))
