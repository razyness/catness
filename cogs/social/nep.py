import sqlite3
import discord
import aiosqlite
import time

import datetime
from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice


class Rep(commands.Cog):
	def __init__(self, ce):
		super().__init__()
		self.ce = ce

		# Connect to the SQLite database
		self.conn = sqlite3.connect('data/rep.db')
		self.cur = self.conn.cursor()

		# Create the table if it doesn't exist
		self.cur.execute('''CREATE TABLE IF NOT EXISTS rep
							(user_id INTEGER, rep INTEGER, time INTEGER)''')
		self.conn.commit()
		print("🟦 rep.db connected")

	@app_commands.command(name="rep", description="Tatsu copied me")
	async def rep(self, inter, user:discord.User):
		if inter.user == user:
			await inter.response.send_message("You can't rep yourself! That'd be a little weird")
			return
		if user.bot:
			await inter.response.send_message("You can't rep bots! End of line")
			return

		async with aiosqlite.connect('data/rep.db') as db:
			db.row_factory = aiosqlite.Row
			rcursor = await db.execute("SELECT * FROM rep WHERE user_id = ?", (inter.user.id,))
			ruser = await rcursor.fetchone()
			mcursor = await db.execute("SELECT * FROM rep WHERE user_id = ?", (user.id,))
			muser = await mcursor.fetchone()
			if muser is None:
				await mcursor.execute("INSERT INTO rep (user_id, rep, time) VALUES (?, 0, 0)", (user.id,))
				await db.commit()
				muser = await mcursor.fetchone()
			if ruser is None:
				await rcursor.execute("INSERT INTO rep (user_id, rep, time) VALUES (?, 0, 0)", (inter.user.id,))
				await db.commit()
				ruser = await rcursor.fetchone()

			expiration_time = datetime.datetime.fromtimestamp(ruser['time']) + datetime.timedelta(hours=12)
			
			if expiration_time < datetime.datetime.now() or inter.user.id == 809275012980539453:
				await mcursor.execute("UPDATE rep SET rep=? WHERE user_id=?", (muser['rep']+1, user.id))
				await rcursor.execute("UPDATE rep SET time=? WHERE user_id=?", (int(time.time()), inter.user.id))
				await db.commit()
				await inter.response.send_message(f"You gave {user.mention} a reputation point!!")
			else:
				await inter.response.send_message(f"You don't have any reputation points left! Return <t:{int(datetime.datetime.timestamp(expiration_time))}:R>")



async def setup(ce):
	await ce.add_cog(Rep(ce))
