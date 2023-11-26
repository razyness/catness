from discord.ext import commands, tasks
from discord import app_commands

import asyncpg

class PGTools(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	async def cog_load(self):
		if not self.remove_guilds.is_running():
			self.remove_guilds.start()

	@commands.Cog.listener("on_guild_remove")
	async def remove_guild(self, guild):
		async with self.bot.db_pool.acquire() as conn:
			try:
				await conn.execute("DELETE FROM servers WHERE id = $1", guild.id)
				print(
					f"📤 I have left the guild {guild.name} | {guild.id}, and removed it from my database")
			except asyncpg.exceptions.PostgresError as e:
				print(
					f"🟥 I could not remove the guild {guild.name} | {guild.id} from my database:", e)

	@commands.Cog.listener("on_guild_join")
	async def add_guild(self, guild):
		async with self.bot.db_pool.acquire() as conn:
			try:
				await conn.execute("INSERT INTO servers (id) VALUES ($1)", guild.id)
				print(
					f"📥 I have joined the guild {guild.name} | {guild.id}, and added it to my database")
			except asyncpg.exceptions.PostgresError as e:
				print(
					f"🟥 I could not add the guild {guild.name} | {guild.id} to my database:", e)
	
	@tasks.loop(hours=24)
	async def remove_guilds(self):
		async with self.bot.db_pool.acquire() as conn:
			db_guilds = await conn.fetch("SELECT id FROM servers")

		db_guild_ids = {record['id'] for record in db_guilds}
		fetched_guilds = {guild async for guild in self.bot.fetch_guilds()}

		for guild in fetched_guilds:
			if guild.id not in db_guild_ids:
				async with self.bot.db_pool.acquire() as conn:
					try:
						await conn.execute("INSERT INTO servers (id) VALUES ($1)", guild.id)
						print(f"➕ I was added to the guild {guild.name} | {guild.id}, and added it to my database")
					except asyncpg.exceptions.PostgresError as e:
						if "duplicate key value violates unique constraint" in str(e):
							continue
						print("[PGLOOP ERROR]")
						print(f"🟧 I could not add the guild {guild.name} | {guild.id} to my database:", e)

		for db_guild_id in db_guild_ids:
			if db_guild_id not in [guild.id for guild in fetched_guilds]:
				async with self.bot.db_pool.acquire() as conn:
					try:
						await conn.execute("DELETE FROM servers WHERE id = $1", db_guild_id)
						print(f"➖ I was removed from the guild with ID {db_guild_id}, and removed it from my database")
					except asyncpg.exceptions.PostgresError as e:
						print("[PGLOOP ERROR]")
						print(f"🟧 I could not remove the guild with ID {db_guild_id} from my database:", e)


async def setup(bot) -> None:
	await bot.add_cog(PGTools(bot))