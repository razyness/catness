import aiosqlite
import random
import discord
import typing

from discord import app_commands
from data import Data, DATABASE_FILE
from discord.ext import commands


class Levels(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.load_db = Data.load_db
		self._cd = commands.CooldownMapping.from_cooldown(1, 6.0, commands.BucketType.member) 

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
		bar = self.generate_progress_bar(max_value=missing, progress_value=exp, level=level)
		embed.description = f"```{bar}```"
		
		await inter.response.send_message(embed=embed)



async def setup(ce):
	await ce.add_cog(Levels(ce))
