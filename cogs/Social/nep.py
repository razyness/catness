import discord
import time
import datetime

from discord import app_commands
from discord.ext import commands


class Rep(commands.Cog):
	def __init__(self, bot):
		super().__init__()
		self.bot = bot
		
	@app_commands.command(name='rep', description="Tatsu copied me")
	async def rep(self, inter, user:discord.User):
		if user == inter.user:
			return await inter.response.send_message("You can't rep yourself! That'd be a little weird", ephemeral=True)
		elif user.bot:
			return await inter.response.send_message("You can't rep bots. End of line.", ephemeral=True)
		
		async with self.bot.db_pool.acquire() as connection:
			async with connection.transaction():
				muser = await connection.fetchrow("SELECT * FROM profiles WHERE id = $1", user.id)
				if muser is None:
					await connection.execute("INSERT INTO profiles (id, rep_value, rep_time) VALUES ($1, 0, 0)", user.id)
					muser = await connection.fetchrow("SELECT * FROM profiles WHERE id = $1", user.id)
	
				ruser = await connection.fetchrow("SELECT * FROM profiles WHERE id = $1", inter.user.id)
				if ruser is None:
					await connection.execute("INSERT INTO profiles (id, rep_value, rep_time) VALUES ($1, 0, 0)", inter.user.id)
					ruser = await connection.fetchrow("SELECT * FROM profiles WHERE id = $1", inter.user.id)

				expiration_time = datetime.datetime.utcfromtimestamp(ruser['rep_time']) + datetime.timedelta(hours=12)
	
				if expiration_time < datetime.datetime.utcnow() or inter.user.id == 1161982476143575051:
					await connection.execute("UPDATE profiles SET rep_value = rep_value + 1 WHERE id = $1", user.id)
					await connection.execute("UPDATE profiles SET rep_time = $1 WHERE id = $2", int(time.time()), inter.user.id)
					await inter.response.send_message(f"You gave {user.mention} a reputation point!!")
				else:
					await inter.response.send_message(f"You don't have any reputation points left! Return <t:{int(datetime.datetime.timestamp(expiration_time))}:R>", ephemeral=True)
			
async def setup(bot):
	await bot.add_cog(Rep(bot))