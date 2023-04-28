import aiosqlite
import discord

from discord import ui
from discord.ext import commands
from discord import app_commands

from data import Data, DATABASE_FILE


class GenMenu(ui.View):
	def __init__(self, user, settings):
		super().__init__()
		self.value = None
		self.user = user
		self.settings = settings

		for i in self.children:
			i.style = self.colorize(
				self.settings[i.label.lower().replace("visibility", "private")])
	
	def colorize(self, value):
		if str(value) == "1":
			print("green")
			return discord.ButtonStyle.green
		print("red")
		return discord.ButtonStyle.red

	@ui.button(label="Visibility", style=discord.ButtonStyle.gray)
	async def vis_button(self, inter, button):
		async with aiosqlite.connect(DATABASE_FILE) as db:
			value = 0
			if self.settings['private'] == 0:
				value = 1
			await db.execute(f"UPDATE settings SET private=? WHERE user_id=?", (value, self.user.id))
			await db.commit()
		self.settings = await Data.load_db(table="settings", user_id=self.user.id)
		button.style = self.colorize(value=self.settings['private'])
		await inter.response.edit_message(view=self)


class SettingsMenu(ui.View):
	def __init__(self, user):
		super().__init__()
		self.value = None
		self.user = user
		self.settings = None

	async def interaction_check(self, interaction) -> bool:
		self.settings = await Data.load_db(table="settings", user_id=self.user.id)
		return True

	async def general_menu(self, settings: dict):
		embed = discord.Embed()
		embed.title = "🔩 General"

		embed.add_field(name=f"Visibility: {str(self.settings['private']).replace('0', '`Shown`').replace('1', '`Hidden`')}",
						value="Your tag won't be shown on leaderboards and other commands showing your user id / discriminator")
		embed.add_field(name=f"Levels: {str(self.settings['levels']).replace('0', '`Disabled`').replace('1', '`Enabled`')}",
						value="Disabling levels will prevent you from gaining xp and leveling up")
		embed.set_footer(text="Select a value to toggle")
		return embed

	async def main_menu(self):
		embed = discord.Embed(title=str(self.user))
		embed.description = "Select an option to pick a category"
		embed.add_field(name="🔩 General",
						value="• Visibility\n• Levels", inline=True)
		embed.add_field(name="🎂 Social",
						value="• Birth year\n• Handles\n", inline=True)
		embed.add_field(name="🧰 Advanced",
						value="• Experiments\n• Reset data", inline=True)
		embed.set_footer(text="Select a value to toggle")
		return embed

	async def social_menu(self):
		embed = discord.Embed()
		embed.title = "🎂 Social"
		birthday = await Data.load_db(table="profiles", user_id=self.user.id, columns=["cake"])
		year_bool = birthday['cake'].split(":")[1]

		embed.add_field(name=f"Birth year: {str(year_bool).replace('True', '`Shown`').replace('False', '`Hidden`')}",
						value="Hiding your birth year will not reveal your age in reminders"
						"and will hide it from your profile.\nRun </unlink:1080271956496101467> to remove your birthday")
		embed.add_field(name=f"Handles: {str(self.settings['handles']).replace('0', '`Shown`').replace('1', '`Hidden`')}",
						value="Hiding handles will only allow you to run related commands with no arguments")
		embed.set_footer(text="Select a value to toggle")
		return embed

	async def advanced_menu(self):
		embed = discord.Embed()
		embed.title = "🎂 Social"

		embed.add_field(name=f"Experiments: {str(self.settings['experiments']).replace('0', '`Disabled`').replace('1', '`Enabled`')}",
						value="Experiments will give you access to broken, unfinished test features. Enable if you're fine with bugs!")
		embed.add_field(name="Reset data", value=":warning: *Cannot be undone!*\nDelete all your data including ranks, handles and everything we know about you.\nThere will be a confirmation dialog, your last chance!")
		embed.set_footer(text="Select a value to toggle")
		return embed

	@ui.button(label="General", emoji="🔩", style=discord.ButtonStyle.blurple)
	async def general_button(self, inter, button):
		embed = await self.general_menu(self.settings)
		await inter.response.defer()
		await self.msg.edit(embed=embed, view=GenMenu(inter.user, self.settings))

	@ui.button(label="Social", emoji="🎂", style=discord.ButtonStyle.blurple)
	async def social_button(self, inter, button):
		embed = await self.social_menu()
		await inter.response.defer()
		await self.msg.edit(embed=embed)

	@ui.button(label="Advanced", emoji="🧰", style=discord.ButtonStyle.blurple)
	async def advanced_button(self, inter, button):
		embed = await self.advanced_menu()
		await inter.response.defer()
		await self.msg.edit(embed=embed)


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

		menu = SettingsMenu(interaction.user)
		embed = await menu.main_menu()
		await interaction.response.send_message(embed=embed, view=menu, ephemeral=True)
		menu.msg = await interaction.original_response()


async def setup(ce: commands.Bot):
	await ce.add_cog(Settings(ce))
