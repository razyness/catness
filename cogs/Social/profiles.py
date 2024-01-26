import discord
import utils
import calendar
import json

from utils import icons, blocking

from datetime import datetime
from discord import app_commands
from discord.ext import commands


class RemoveView(discord.ui.View):
	def __init__(self, profile_user, inter_user, db_pool):
		super().__init__()
		self.value = None
		self.profile_user = profile_user
		self.inter_user = inter_user
		self.db_pool = db_pool

	async def remove_birthday(self, profile_user, inter_user):
		async with self.db_pool.acquire() as conn:
			async with conn.transaction():
				inter_user_data = await conn.fetchrow("SELECT follows FROM profiles WHERE id = $1", inter_user.id)
				profile_user_data = await conn.fetchrow("SELECT follows FROM profiles WHERE id = $1", profile_user.id)

				inter_data = await blocking.run(lambda: json.loads(inter_user_data['follows']))
				profile_data = await blocking.run(lambda: json.loads(profile_user_data['follows']))

				if profile_user.id in inter_data['following'] and inter_user.id in profile_data['followers']:
					inter_data['following'].remove(profile_user.id)
					inter_data = await blocking.run(lambda: json.dumps(inter_data))

					profile_data['followers'].remove(inter_user.id)
					profile_data = await blocking.run(lambda: json.dumps(profile_data))

					await conn.execute("UPDATE profiles SET follows = $1 WHERE id = $2", inter_data, inter_user.id)
					await conn.execute("UPDATE profiles SET follows = $1 WHERE id = $2", profile_data, profile_user.id)


	@discord.ui.button(label="Cancel", emoji=icons.remove, style=discord.ButtonStyle.red)
	async def remove_cake(self, inter, button):
		await self.remove_birthday(self.profile_user, self.inter_user)
		await inter.response.send_message(f"You will not be notified on {self.profile_user.mention}'s birthday", ephemeral=True)


class ProfileView(utils.ui.View):
	def __init__(self, bot, user, inter, owned):
		super().__init__(inter, owned)
		self.value = None
		self.bot = bot
		self.profile_user = user

	async def notify_action(self, profile_user, inter_user):
		async with self.bot.db_pool.acquire() as conn:
			async with conn.transaction():
				inter_user_data = await conn.fetchrow("SELECT follows FROM profiles WHERE id = $1", inter_user.id)

				if inter_user_data is None:
					await conn.execute("INSERT INTO profiles (id, follows) VALUES ($1, $2)", inter_user.id, {"followers": [], "following": []})
					inter_user_data = await conn.fetchrow("SELECT follows FROM profiles WHERE id = $1", inter_user.id)

				profile_user_data = await conn.fetchrow("SELECT follows FROM profiles WHERE id = $1", profile_user.id)

				inter_data = await blocking.run(lambda: json.loads(inter_user_data['follows']))
				profile_data = await blocking.run(lambda: json.loads(profile_user_data['follows']))

				if profile_user.id not in inter_data['following'] and inter_user.id not in profile_data['followers']:
					inter_data['following'].append(profile_user.id)
					inter_data = await blocking.run(lambda: json.dumps(inter_data))

					profile_data['followers'].append(inter_user.id)
					profile_data = await blocking.run(lambda: json.dumps(profile_data))

					await conn.execute("UPDATE profiles SET follows = $1 WHERE id = $2", inter_data, inter_user.id)
					await conn.execute("UPDATE profiles SET follows = $1 WHERE id = $2", profile_data, profile_user.id)

					return f"You will be notified on {self.profile_user.mention}'s birthday !!"
				else:
					return f"You are already following {self.profile_user.mention}'s birthday (frown, loser)"

	@discord.ui.button(label="Notify me!", emoji="🎂", style=discord.ButtonStyle.blurple)
	async def notify(self, inter, button):
		resp = await self.notify_action(self.profile_user, inter.user)
		view = RemoveView(self.profile_user, inter.user, self.bot.db_pool)
		if inter.user.id == self.profile_user.id:
			return await inter.response.send_message("You can't follow your own birthday, you should remember it i think", ephemeral=True)
		await inter.response.send_message(resp, view=view, ephemeral=True)


class Profile(commands.Cog):
	def __init__(self, bot) -> None:
		super().__init__()
		self.bot = bot

	@app_commands.command(name='profile', description='View anyone\'s profile almost')
	@app_commands.describe(user="Hello pick a user or user id or mention leave empty for yourself")
	async def discord_id(self, interaction, user: str = None, ephemeral:bool=False):
		if user is None:
			user = interaction.user.id
		elif user.startswith("<@"):
			user = int(user[2:-1])
		try:
			user = await self.bot.fetch_user(int(user))
		except:
			return await interaction.response.send_message("The user you entered is invalid :(", ephemeral=True)

		view = ProfileView(self.bot, user, interaction, False)

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
		if user.id in self.bot.config["ids"]["contributors"]:
			badges_list.append(f'[{icons.contributor}](https://github.com/razyness/catness)')
		if user.id in self.bot.config["ids"]["special"]:
			badges_list.append(icons.special)

		result = ' '.join(badges_list)
		embed.description = result

		if user.bot:
			for i in view.children:
				if not i.url:
					view.remove_item(i)

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

				cake = await conn.fetchval("SELECT cake FROM profiles WHERE id = $1", user.id)
				if cake:
					cake = await blocking.run(lambda: json.loads(cake))
					if cake['consider']:
						value = discord.utils.format_dt(datetime(cake['year'], cake['month'], cake['day']), style='D')
					else:
						value = f"`{calendar.month_name[cake['month']]} {cake['day']}`"
					embed.add_field(name='Birthday', value=value)
				else:
					for i in view.children:
						if not i.url:
							view.remove_item(i)

				level = await conn.fetchval("SELECT level FROM profiles WHERE id = $1", user.id)
				exp = await conn.fetchval("SELECT exp FROM profiles WHERE id = $1", user.id)
				
				if (level, exp) != (0, 0):
					embed.add_field(name='Rank', value=f'Level `{level}` | `{exp}`xp')

		await interaction.response.send_message(embed=embed, ephemeral=ephemeral, view=view)
		view.message = await interaction.original_response()

async def setup(bot):
	await bot.add_cog(Profile(bot))
