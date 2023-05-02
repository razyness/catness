from typing import Optional, List
import aiosqlite
import random
import discord
import typing

from discord import app_commands, ui
from discord.interactions import Interaction
from data import Data, DATABASE_FILE
from discord.ext import commands
from collections import deque

class Paginateness(ui.View):
	def __init__(self, embeds:List[discord.Embed]) -> None:
		super().__init__(timeout=180)

		self._embeds = embeds
		self._queue = deque(embeds)
		self._initial = embeds[0]
		self._length = len(embeds)
		self._current_page = 1
		self._queue[0].set_footer(text=f"Page {self._current_page} of {self._length}")

		self.children[0].disabled = True

		if self._length == 1:
			self.children[1].disabled = True

	async def update_buttons(self, inter):
		for i in self._queue:
			i.set_footer(text=f"Page {self._current_page} of {self._length}")

		if self._current_page == self._length:
			self.children[1].disabled = True
		else:
			self.children[1].disabled = False

		if self._current_page == 1:
			self.children[0].disabled = True
		else:
			self.children[0].disabled = False

		await inter.response.edit_message(view=self)

	@ui.button(label="<", style=discord.ButtonStyle.blurple)
	async def prev(self, inter, button):
		self._queue.rotate(-1)
		self._current_page -= 1
		embed = self._queue[0]

		await self.msg.edit(embed=embed)
		await self.update_buttons(inter)

	@ui.button(label=">", style=discord.ButtonStyle.blurple)
	async def next(self, inter, button):
		self._queue.rotate(1)
		self._current_page += 1
		embed = self._queue[0]
		
		await self.msg.edit(embed=embed)
		await self.update_buttons(inter)

	@property
	def initial(self) -> discord.Embed:
		return self._initial


class Levels(commands.Cog):
	def __init__(self, ce):
		self.ce = ce
		self.load_db = Data.load_db
		self._cd = commands.CooldownMapping.from_cooldown(
			1, 6.0, commands.BucketType.member)

	def experience_curve(self, level) -> int:
		return round(5 * (level ** 2) + (50 * level) + 100)

	async def update_user(self, user_id, exp):
		async with aiosqlite.connect(DATABASE_FILE) as db:
			row = await self.load_db(table='profiles', user_id=user_id, columns=["level", "exp"])
			level, current_exp = row["level"], row["exp"]
			new_exp = current_exp + exp

			while new_exp >= self.experience_curve(level):
				new_exp -= self.experience_curve(level)
				level += 1

			await db.execute("UPDATE profiles SET exp=?, level=? WHERE user_id=?", (new_exp, level, user_id,))
			await db.commit()

	async def get_level(self, user_id):
		row = await self.load_db(table='profiles', user_id=user_id, columns=["level"])
		return row["level"]

	async def get_exp(self, user_id):
		row = await self.load_db(table='profiles', user_id=user_id, columns=["exp"])
		return row["exp"]

	def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
		bucket = self._cd.get_bucket(message)
		return bucket.update_rate_limit()

	@commands.Cog.listener("on_message")
	async def give_xp(self, message):
		ratelimit = self.get_ratelimit(message)
		if message.author.bot or ratelimit is not None:
			return
		user_id = message.author.id
		prev_level = await self.get_level(user_id)
		prev_exp = await self.get_exp(user_id)
		xp_given = random.randint(5, 15)
		await self.update_user(user_id, xp_given)
		new_exp = prev_exp + xp_given
		exp_needed = self.experience_curve(prev_level)
		if new_exp >= exp_needed:
			new_level = prev_level + 1
			async with aiosqlite.connect(DATABASE_FILE) as db:
				await db.execute("UPDATE profiles SET level=? WHERE user_id=?", (new_level, user_id,))
				await db.commit()
			if new_level > prev_level:
				await message.channel.send(f"{message.author.mention} is now level `{new_level}`! Your new goal is `{self.experience_curve(new_level)}`")

	def generate_progress_bar(self, max_value, progress_value, level):
		percent_progress = progress_value / max_value
		filled_chars = round(percent_progress * 30)
		progress_bar = "▮" * filled_chars + "▯" * (30 - filled_chars)
		max_value_str = f"{max_value}"
		xp_level_str = f" xp: {progress_value}/{max_value}{' '*(13-len(max_value_str)-len(str(progress_value)))}level: {level} -> {level + 1}"
		output_str = f"{xp_level_str}\n{' '}{progress_bar}"
		return output_str

	@app_commands.command()
	async def rank(self, inter):
		embed = discord.Embed(title=str(inter.user))
		embed.set_thumbnail(url=inter.user.avatar.url)

		levels_info = await Data.load_db(table="profiles", user_id=inter.user.id, columns=["level", "exp"])
		level, exp = levels_info["level"], levels_info["exp"]
		missing = round(5 * (level ** 2) + (50 * level) + 100)
		bar = self.generate_progress_bar(
			max_value=missing, progress_value=exp, level=level)
		embed.description = f"```{bar}```"

		await inter.response.send_message(embed=embed)

	@app_commands.command(name="top", description="Leaderboard of sorts and stuffs")
	@app_commands.describe(compact="Show less users per page, to fit on mobile")
	async def top(self, inter, compact:bool=False):
		compact = 6 if compact else 12
		conn = await aiosqlite.connect(DATABASE_FILE)
		cursor = await conn.cursor()

		await cursor.execute("SELECT user_id, level, exp FROM profiles")
		rows = await cursor.fetchall()

		profile_list = []

		for row in rows:
			user_id, level, exp = row
	
			settings = await Data.load_db(table="settings", user_id=user_id)
			user = str(self.ce.get_user(user_id) or await self.ce.fetch_user(user_id))
			if settings['private'] == 1:
				user = f"{user[:-4]}????"

			profile_dict = {
				'user': user,
				'level': level,
				'exp': exp
			}

			if settings['levels'] != 0:
				profile_list.append(profile_dict)

			if len(profile_list) >= 50:
				break

		await conn.close()

		profile_list = sorted(profile_list, key=lambda x: x['level'] + x['exp'] / (100 * len(str(x['exp']))), reverse=True)

		embeds = []
		pos = 1
		for i in range(0, len(profile_list), compact):
			embed = discord.Embed(title="Leaderboard of the levels real")

			for profile in profile_list[i:i+compact]:
				user = profile['user']
				level = profile['level']
				exp = profile['exp']
				flair = f"{pos}"
				if pos == 1:
					flair = f"🥇"
				elif pos == 2:
					flair = f"🥈"
				elif pos == 3:
					flair = f"🥉"
				embed.add_field(name=f"{flair}. {user}", value=f"Level `{level}`/`{exp}`xp")
				pos += 1

			embeds.append(embed)
		
		view = Paginateness(embeds)
		await inter.response.send_message(embed=view.initial, view=view)
		view.msg = await inter.original_response()

async def setup(ce):
	await ce.add_cog(Levels(ce))
