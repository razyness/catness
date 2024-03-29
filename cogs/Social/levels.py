import random
import discord
import requests
import asyncio
import io
import easy_pil
import math

from PIL import Image

from discord import app_commands
from discord.ext import commands, tasks

from utils import blocking, pager


async def get_user_position(bot, user_id):
	query = """
		SELECT
			CASE
				WHEN EXISTS (SELECT 1 FROM profiles WHERE id = $1)
				THEN (
					SELECT COUNT(*) + 1
					FROM profiles
					WHERE (level, exp) > (SELECT level, exp FROM profiles WHERE id = $1 AND levels_enabled = true)
				)
				ELSE 0
			END;
	"""
	async with bot.db_pool.acquire() as conn:
		position = await conn.fetchval(query, user_id)
	return position


def get_image(url):
	response = requests.get(url)
	if response.status_code != 200:
		raise ValueError(
			f"Failed to fetch image, status code: {response.status_code}")
	image_data = response.content
	image = Image.open(io.BytesIO(image_data))
	return image


def create_card(user_data):
	background = get_image(user_data['banner'])
	empty_canvas = easy_pil.Canvas(size=(1000, 620), color=(0, 0, 0, 0))
	editor = easy_pil.Editor(image=background)
	editor.resize(size=(1000 // 2, 620 // 2 - 40), crop=True)

	blur_editor = easy_pil.Editor(image=empty_canvas)

	profile_shadow_editor = easy_pil.Editor(image=empty_canvas)
	profile_shadow = profile_shadow_editor.rectangle(position=(
		98 // 2, 98 // 2), width=287 // 2, height=287 // 2, color=(0, 0, 0, 90), radius=40 // 2)
	blur_editor.paste(profile_shadow, (0, 0 - 10))

	gradient_editor = easy_pil.Editor(image=empty_canvas)
	gradient = gradient_editor.rectangle(position=(
		0, 0), width=1000 // 2, height=600 // 2, color=(0, 0, 0, 30), radius=0)
	editor.paste(gradient, (0, 0 - 10))

	rep_blur_editor = easy_pil.Editor(image=empty_canvas)
	rep_shadow = rep_blur_editor.bar(position=(
		682 // 2, 333 // 2), max_width=205 // 2, height=57 // 2, percentage=100, color=(0, 0, 0, 90), radius=15 // 2)
	blur_editor.paste(rep_shadow, (0, 0 - 10))

	text_editor = easy_pil.Editor(image=empty_canvas)
	font_large = easy_pil.Font.montserrat(size=45 // 2, variant="bold")
	font_medium = easy_pil.Font.montserrat(size=32 // 2, variant="bold")
	font_small = easy_pil.Font.poppins(size=30 // 2, variant="bold")

	username = text_editor.text(position=(
		433 // 2, 133 // 2), text=user_data["name"], color=(0, 0, 0, 90), font=font_large)
	exp_text = text_editor.text(position=(
		104 // 2, 468 // 2), text=f'{user_data["xp"]}/{user_data["next_level_xp"]}', color=(0, 0, 0, 90),
		font=font_small)
	level_text = text_editor.text(position=(
		880 // 2, 468 // 2), text=f'{user_data["level"]} > {user_data["level"] + 1}', color=(0, 0, 0, 90),
		align="right", font=font_small)
	position_shadow = text_editor.text(position=(
		880 // 2, 133 // 2), text=user_data['position'], color=(0, 0, 0, 90), align="right", font=font_large)

	blur_editor.paste(username, (0, 0 - 10))
	blur_editor.paste(exp_text, (0, 0 - 10))
	blur_editor.paste(level_text, (0, 0 - 10))

	bar_editor = easy_pil.Editor(image=empty_canvas)
	bar_shadow = bar_editor.bar(position=(98 // 2, 404 // 2), max_width=787 // 2,
								height=57 // 2, percentage=100, color=(0, 0, 0, 90), radius=15 // 2)

	blur_editor.paste(position_shadow, (0, 0 - 10))

	blur_editor.paste(bar_shadow, (0, 0 - 10))

	blur_editor.blur(mode="gussian", amount=20 // 2)

	editor.paste(blur_editor, (0, 5))

	bar = bar_editor.bar(position=(98 // 2, 404 // 2), max_width=787 // 2, height=57 // 2,
						 percentage=100, color=(255, 255, 255, 70), radius=15 // 2)
	editor.paste(bar, (0, 0 - 10))
	bar_progress = bar_editor.bar(position=(98 // 2, 404 // 2), max_width=787 // 2, height=57 // 2,
								  percentage=user_data['percentage'], color=(255, 255, 255, 230), radius=15 // 2)
	editor.paste(bar_progress, (0, 0 - 10))

	rep_bg_editor = easy_pil.Editor(image=empty_canvas)
	rep_bg = rep_bg_editor.bar(position=(682 // 2, 333 // 2), max_width=205 // 2,
							   height=57 // 2, percentage=100, color=(255, 255, 255, 180), radius=15 // 2)
	editor.paste(rep_bg, (0, 0 - 10))

	avatar_image = get_image(user_data['avatar'])
	avatar = easy_pil.Editor(avatar_image).resize(
		(287 // 2, 287 // 2)).rounded_corners(radius=40 // 2)
	editor.paste(avatar, (98 // 2, 98 // 2 - 10))

	username = text_editor.text(position=(
		433 // 2, 133 // 2), text=user_data["name"], color=(255, 255, 255, 200), font=font_large)
	exp_text = text_editor.text(position=(
		104 // 2, 468 // 2), text=f'{user_data["xp"]}/{user_data["next_level_xp"]}', color=(255, 255, 255, 140),
		font=font_small)
	level_text = text_editor.text(position=(
		880 // 2, 468 // 2), text=f'{user_data["level"]} > {user_data["level"] + 1}', color=(255, 255, 255, 140),
		align="right", font=font_small)
	rep_text = text_editor.text(position=(
		782 // 2, 350 // 2), text=f"+ {user_data['rep']} rep", color=(30, 30, 30), align="center", font=font_medium)

	position_text = text_editor.text(position=(
		880 // 2, 133 // 2), text=user_data['position'], color=(255, 255, 255, 200), align="right", font=font_large)

	editor.paste(position_text, (0, 0 - 10))
	editor.paste(username, (0, 0 - 10))
	editor.paste(exp_text, (0, 0 - 10))
	editor.paste(level_text, (0, 0 - 10))
	editor.paste(rep_text, (0, 0 - 10))

	return editor.image_bytes


class Levels(commands.Cog):
	"""
	Levels and stuff :3 Enable rank cars with experiments"""

	def __init__(self, bot):
		self.bot = bot
		self.cooldowns = commands.CooldownMapping.from_cooldown(
			1, 15.0, commands.BucketType.user)

	class Entry():
		def __init__(self, user_id, name, level, exp, rank):
			self.id = user_id
			self.name = name
			self.level = level
			self.exp = exp
			self.rank = rank

	def cog_unload(self):
		self.refresh_leaderboard.stop()

	def cog_load(self):
		self.refresh_leaderboard.start()

	def experience_curve(self, level) -> int:
		return round(5 * (level ** 2) + (50 * level) + 100, -1)

	def generate_progress_bar(self, max_value, progress_value, level):
		percent_progress = progress_value / max_value
		filled_chars = round(percent_progress * 30)
		progress_bar = "▮" * filled_chars + "▯" * (30 - filled_chars)
		max_value_str = f"{max_value}"
		xp_level_str = f" xp: {progress_value}/{max_value}{' ' * (13 - len(max_value_str) - len(str(progress_value)))}level: {level} -> {level + 1}"
		output_str = f"{xp_level_str}\n{' '}{progress_bar}"
		return output_str

	@tasks.loop(hours=1)
	async def refresh_leaderboard(self):
		limit = 100

		query = """
			SELECT ROW_NUMBER() OVER (ORDER BY level DESC, exp DESC, id DESC) AS rank, id, exp, level, profiles.profile_private
			FROM profiles
			WHERE exp > 0 AND level > 0 AND levels_enabled = true
			FETCH FIRST $1 ROWS ONLY
		"""
		count_query = """
			SELECT COUNT(*) FROM (
				SELECT 1 FROM profiles WHERE exp > 0 AND level > 0 AND levels_enabled = true
			) AS subquery
		"""

		async with self.bot.db_pool.acquire() as conn:
			rows = await conn.fetch(query, limit)
			total_rows = await conn.fetchval(count_query)

		cached_leaderboard = {"total_entries": total_rows, "entries": []}

		top_3 = ["🥇", "🥈", "🥉"]

		for i, row in enumerate(rows):
			rank, user_id, exp, level, profile_private = row
			user = await self.bot.get_or_fetch_user(user_id)

			name = user.global_name if profile_private else user.name

			if i < 3:
				name = top_3[i] + name

			cached_leaderboard["entries"].append(
				self.Entry(user.id, name, level, exp, rank))

		self.bot.cached_leaderboard = cached_leaderboard

	@commands.Cog.listener("on_message")
	async def give_xp(self, message):
		if message.author.bot or not message.guild:
			return

		bucket = self.cooldowns.get_bucket(message)
		retry_after = bucket.update_rate_limit()
		if retry_after:
			return

		async with self.bot.db_pool.acquire() as conn:
			async with conn.transaction():
				user_data = await conn.fetchrow("SELECT * FROM profiles WHERE id = $1", message.author.id)
				server_data = await conn.fetchrow("SELECT * FROM servers WHERE id = $1", message.guild.id)
				if user_data is None:
					await conn.execute("INSERT INTO profiles (id, exp, level) VALUES ($1, $2, $3)", message.author.id,
									   1, 0)
				elif not user_data['levels_enabled'] or not server_data['levels_enabled']:
					return
				else:
					xp_to_add = random.randint(5, 20)
					xp_required = self.experience_curve(
						user_data['level'])

					if user_data['exp'] + xp_to_add >= xp_required:
						await conn.execute("UPDATE profiles SET exp = $1 WHERE id = $2",
										   user_data['exp'] + xp_to_add - xp_required, message.author.id)
						await conn.execute("UPDATE profiles SET level = $1 WHERE id = $2", user_data['level'] + 1,
										   message.author.id)
						emoji = random.choice(
							["🌞", "🌻", "🌼", "🎉", "🎊", "🎇", "🎁", "📚", "📬", "💌", "🎶", "<:angle:1154534259462262815>", "🎈",
							 "🎄", "🕊️", "⭐", "🍀"])
						embed = discord.Embed(
							title=f"{emoji} You leveled up to **{user_data['level'] + 1}**!")
						embed.set_footer(
							text=f"You'll need {self.experience_curve(user_data['level'] + 1)}xp to level up again")
						await message.reply(embed=embed, delete_after=60)
					else:
						await conn.execute("UPDATE profiles SET exp = $1 WHERE id = $2", user_data['exp'] + xp_to_add,
										   message.author.id)

	@app_commands.command(description="Display your total XP and the amount of XP needed to reach the next level.")
	@app_commands.describe(user="i think you can figure it out")
	async def rank(self, inter, user: discord.User = None):
		user = user or inter.user

		position = await get_user_position(self.bot, user.id)
		if position is None:
			return await inter.response.send_message("User not found", ephemeral=True)

		async with self.bot.db_pool.acquire() as conn:
			async with conn.transaction():
				user_info = await conn.fetchrow("SELECT * FROM profiles WHERE id = $1", user.id)
				if user_info is None:
					await conn.execute("INSERT INTO profiles (id) VALUES ($1)", user.id)
					user_info = await conn.fetchrow("SELECT * FROM profiles WHERE id = $1", user.id)

				if not user_info['levels_enabled']:
					return await inter.response.send_message("Their level is turned off!!!!", ephemeral=True)

				user = await self.bot.fetch_user(user.id)
				if user.bot:
					await inter.response.send_message("Bots are not allowed a rank because i'm mean!!!", ephemeral=True)
					return

				if inter.guild:
					server_levels_on = await conn.fetchval("SELECT levels_enabled FROM servers WHERE id = $1",
														   inter.guild.id)
					if server_levels_on == 0:
						return await inter.response.send_message("Levels are disabled in this server", ephemeral=True)

				level, exp = user_info["level"], user_info["exp"]
				missing = self.experience_curve(level)

		if user_info['tests_enabled'] == 1:
			user_data = {
				"name": user.global_name if user_info['profile_private'] else user.name,
				"xp": exp,
				"next_level_xp": missing,
				"level": level,
				"percentage": (exp / missing) * 100,
				"rep": user_info["rep_value"],
				"avatar": user.display_avatar.url,
				"banner": f"{user.banner.url[:-9]}?size=1024" if user.banner else "https://cdn.discordapp.com/attachments/912099940325523586/1104016078880919592/card.png",
				"position": f"#{position}" if position > 0 else "Unranked",
			}

			await inter.response.defer(thinking=True)
			card = await blocking.run(lambda: create_card(user_data=user_data))

			file = discord.File(fp=card, filename='card.png')
			await inter.followup.send(file=file)
		else:
			embed = discord.Embed(title=str(user))
			embed.set_thumbnail(url=user.display_avatar.url)
			bar = self.generate_progress_bar(
				max_value=missing, progress_value=exp, level=level)

			if position == 0:
				embed.description = f"You are not ranked. Not neat."
			else:
				embed.description = f"Your position is `#{position}`. Neat!"
			embed.description += f"\n```{bar}```"
			await inter.response.send_message(embed=embed)

	@app_commands.command(name="top", description="Leaderboard of sorts and stuffs")
	@app_commands.describe(compact="Show less users per page, to fit on mobile")
	async def top(self, inter: discord.Interaction, compact: bool = False):
		pos = await get_user_position(self.bot, inter.user.id)

		size = 6 if compact else 12
		pages = []

		shown = len(self.bot.cached_leaderboard['entries'])
		total = self.bot.cached_leaderboard['total_entries']

		for _ in range(math.ceil(len(self.bot.cached_leaderboard["entries"]) / size)):
			embed = discord.Embed()
			embed.title = "Leaderboard of the levels real"
			embed.description = f"Your position is `#{pos}`. Neat!\nShowing `{shown}` of `{total}`"
			embed.set_footer(text="The leaderboard updates hourly.")
			pages.append(embed)

		page = 0

		for pos, entry in enumerate(self.bot.cached_leaderboard["entries"]):
			if pos > 0:
				if pos % size == 0:
					page += 1

			pages[page].add_field(
				name=entry.name, value=f"Level `{entry.level}` | `{entry.exp}`xp")

		await pager.Paginator(inter, self.bot, pages).start(ephemeral=False)


async def setup(bot):
	await bot.add_cog(Levels(bot))
