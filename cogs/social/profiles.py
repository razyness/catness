import discord
import time
import calendar
import json

from utils.data import icons

from datetime import datetime
from discord import app_commands
from discord.ext import commands


class RemoveView(discord.ui.View):
	def __init__(self, user, author):
		super().__init__()
		self.value = None
		self.user = user
		self.author = author

	async def remove_birthday(self, user, author):
		async with self.bot.db_pool.acquire() as conn:
			async with conn.transaction():
				user_data = await conn.fetchrow("SELECT follows FROM profiles WHERE id = $1", user.id)
				self_user_data = await conn.fetchrow("SELECT follows FROM profiles WHERE id = $1", author.id)

				user_follows = user_data['follows']
				self_follows = self_user_data['follows']

				if user.id in self_follows['following'] and author.id in user_follows['follow_list']:
					self_follows['following'].remove(user.id)
					user_follows['follow_list'].remove(author.id)

					await conn.execute("UPDATE profiles SET follows = $1 WHERE id = $2", self_follows, user.id)
					await conn.execute("UPDATE profiles SET follows = $1 WHERE id = $2", user_follows, author.id)

	@discord.ui.button(label="Cancel", emoji=icons.remove, style=discord.ButtonStyle.red)
	async def remove_cake(self, inter, button):
		await self.remove_birthday(self.user, self.author)
		await inter.response.send_message(f"You will not be notified on {self.user.mention}'s birthday", ephemeral=True)


class ProfileView(discord.ui.View):
	def __init__(self, bot, user):
		super().__init__()
		self.value = None
		self.bot = bot
		self.user = user

	async def disable_all(self):
		for i in self.children:
			i.disabled = True
		await self.msg.edit(view=self)

	async def on_timeout(self):
		await self.disable_all()

	async def notify_action(self, user, author):
		async with self.bot.db_pool.acquire() as conn:
			async with conn.transaction():
				user_data = await conn.fetchrow("SELECT follows FROM profiles WHERE id = $1", user.id)
				self_user_data = await conn.fetchrow("SELECT follows FROM profiles WHERE id = $1", author.id)

				user_follows = user_data['follows']
				self_follows = self_user_data['follows']

				if user.id in self_follows['following'] and author.id in user_follows['follow_list']:
					self_follows['following'].append(user.id)
					user_follows['follow_list'].append(author.id)

					await conn.execute("UPDATE profiles SET follows = $1 WHERE id = $2", self_follows, user.id)
					await conn.execute("UPDATE profiles SET follows = $1 WHERE id = $2", user_follows, author.id)
					return f"You will be notified on {self.user.mention}'s birthday !!"
				else:
					return f"You are already following {self.user.mention}'s birthday (frown)"

	@discord.ui.button(label="Notify me!", emoji="🎂", style=discord.ButtonStyle.blurple)
	async def notify(self, inter, button):
		resp = await self.notify_action(self.user, inter.user)
		view = RemoveView(self.user, inter.user)
		await inter.response.send_message(resp, view=view, ephemeral=True)

	async def interaction_check(self, interaction) -> bool:
		if interaction.user.id == self.user.id:
			await interaction.response.send_message("You can't follow your own birthday, you should remember it i think", ephemeral=True)
			return False
		return True


class Profile(commands.Cog):
	def __init__(self, bot) -> None:
		super().__init__()
		self.bot = bot

	@app_commands.command(name='profile', description='View anyone\'s profile almost')
	@app_commands.describe(user="Hello pick a user or user id or mention leave empty for yourself")
	async def discord_id(self, interaction, user: str = None):
		if user is None:
			user = interaction.user.id
		elif user.startswith("<@"):
			user = int(user[2:-1])
		try:
			user = self.bot.get_user(int(user)) or await self.bot.fetch_user()
		except:
			return await interaction.response.send_message("The user you entered is invalid :(", ephemeral=True)

		view = ProfileView(self.bot, user)

		view.add_item(discord.ui.Button(
			label='Avatar', style=discord.ButtonStyle.link, url=user.avatar.url, emoji=icons.download))

		embed = discord.Embed(title=user.display_name)
		embed.set_author(name=user.name)
		embed.color = user.accent_color or discord.Color.default()
		embed.set_image(url=user.banner.url if user.banner else None)
		embed.set_thumbnail(url=user.display_avatar)

		if user.banner:
			view.add_item(discord.ui.Button(
				label='Banner', style=discord.ButtonStyle.link, url=user.banner.url, emoji=icons.download))

		embed.add_field(name='Created on',
						value=discord.utils.format_dt(user.created_at, 'R'))

		badges_list = []
		for flag in user.public_flags.all():
			badges_list.append(icons[flag.name])
		if user.avatar.url.startswith("a_") or user.banner is not None:
			badges_list.append(icons.nitro)
		if user.bot:
			badges_list.append(icons.bot)
		if user.id in self.bot.config["contributors"]:
			badges_list.append(f'[{icons.contributor}](https://github.com/razyness/catness)')
		if user.id in self.bot.config["special"]:
			badges_list.append(icons.special)

		result = ' '.join(badges_list)
		embed.description = result

		if user.bot:
			await interaction.response.send_message(embed=embed, view=view)
			view.msg = await interaction.original_response()
			return

		async with self.bot.db_pool.acquire() as conn:
			async with conn.transaction():
				user_exists = await conn.fetchval("SELECT EXISTS(SELECT 1 FROM profiles WHERE id = $1)", user.id)

				if not user_exists:
					await conn.execute("INSERT INTO profiles (id, rep_value) VALUES ($1, 0)", user.id)

				rep = await conn.fetchval("SELECT rep_value FROM profiles WHERE id = $1", user.id)

				embed.add_field(name='Rep nepnep', value=f'`{rep}` points')

				socials = await conn.fetchval("SELECT socials FROM profiles WHERE id = $1", user.id)

				if socials != '{}':
					socials_dict = json.loads(socials)
					socials_list = []
					for key, value in socials_dict.items():
						socials_list.append(f"{icons[key]} `{value}`")
					socials_str = '\n'.join(socials_list)
					embed.add_field(name='Socials', value=socials_str)

		await interaction.response.send_message(embed=embed)


async def setup(bot):
	await bot.add_cog(Profile(bot))
