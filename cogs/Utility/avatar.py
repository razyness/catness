import discord
import asyncio

from discord.ext import commands
from discord import app_commands

from utils import icons

class DownloadButton(discord.ui.View):

	def __init__(self, user):
		super().__init__()
		self.value = None
		self.msg = None
		self.user = user
		self.selection = "Server"

		for child in self.children:
			if child.emoji == icons.close:
				continue

			if self.user.avatar is None and child.label == "Display":
				child.disabled = True
				child.style = discord.ButtonStyle.gray
				self.selection = "Default"

			if child.label == "Server":
				self.selection = "Display"
				child.disabled = True
				child.style = discord.ButtonStyle.gray

			if isinstance(user, discord.Member):
				if self.user.guild_avatar is not None and child.label == "Server":
					child.disabled = False
					child.style = discord.ButtonStyle.blurple
					self.selection = "Server"

		for child in self.children:
			if child.emoji == icons.close or child.style == discord.ButtonStyle.gray:
				continue
			child.disabled = True if child.label == self.selection else False

	async def disable_all(self, msg="Timed out...", view=None):
		for i in self.children:
			i.disabled = True
		await self.msg.edit(content=msg, embed=None, view=view)

	async def on_timeout(self):
		await self.disable_all()

	@discord.ui.button(label="Default", style=discord.ButtonStyle.blurple)
	async def default_avatar(self, inter, button):
		self.selection = button.label
		for child in self.children:
			if child.emoji == icons.close or child.style == discord.ButtonStyle.gray:
				continue
			child.disabled = True if child.label == self.selection else False
		embed = self.msg.embeds[0]
		embed.set_image(url=self.user.default_avatar.url)
		await inter.response.defer()
		await self.msg.edit(embed=embed, view=self)

	@discord.ui.button(label="Display", style=discord.ButtonStyle.blurple)
	async def display_avatar(self, inter, button):
		self.selection = button.label
		for child in self.children:
			if child.emoji == icons.close or child.style == discord.ButtonStyle.gray:
				continue
			child.disabled = True if child.label == self.selection else False
		embed = self.msg.embeds[0]
		embed.set_image(url=self.user.avatar.url)
		await inter.response.defer()
		await self.msg.edit(embed=embed, view=self)

	@discord.ui.button(label="Server", style=discord.ButtonStyle.blurple)
	async def guild_avatar(self, inter, button):
		self.selection = button.label
		for child in self.children:
			if child.emoji == icons.close or child.style == discord.ButtonStyle.gray:
				continue
			child.disabled = True if child.label == self.selection else False
		embed = self.msg.embeds[0]
		embed.set_image(url=self.user.guild_avatar.url)
		await inter.response.defer()
		await self.msg.edit(embed=embed, view=self)

	@discord.ui.button(emoji=icons.close, style=discord.ButtonStyle.red)
	async def close(self, interaction: discord.Interaction, button: discord.ui.Button):

		await self.disable_all(msg="Bye-bye")
		self.value = False
		self.stop()
		await interaction.response.defer()
		await asyncio.sleep(2)
		await self.msg.delete()

	async def interaction_check(self, interaction) -> bool:
		if interaction.user.id != self.author:
			await interaction.response.send_message('This is not your menu, run </avatar:1064683905514487858> to open your own.', ephemeral=True)
			return False
		return True


class Avatar(commands.Cog):
	"""
	Commands related to avatars
	"""
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(name='avatar', description='Get yours/someone\'s avatar')
	@app_commands.describe(user='user hello person avatar')
	async def avatar(self, interaction, user: discord.User = None):
		user = user or interaction.user

		view = DownloadButton(user)

		embed = discord.Embed()
		embed.set_author(name=f'{str(user)}', icon_url=user.avatar.url if user.avatar else user.default_avatar.url)
		embed.set_image(url=user.display_avatar.url)
		await interaction.response.send_message(embed=embed, view=view)
		view.msg = await interaction.original_response()
		view.author = interaction.user.id


async def setup(bot):
	await bot.add_cog(Avatar(bot))
