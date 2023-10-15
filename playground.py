import discord

import asyncio
import asyncpg
import logging
import toml

from typing import List, Optional

from discord.ext import commands
from aiohttp import ClientSession

config = toml.load("./config.toml")


class Client(commands.AutoShardedBot):
	def __init__(
		self,
		*args,
		initial_extensions: List[str],
		db_pool: asyncpg.Pool,
		web_client: ClientSession,
		testing_guild_id: Optional[int],
		config: dict,
		**kwargs
	):
		super().__init__(*args, **kwargs)
		self.db_pool = db_pool
		self.web_client = web_client
		self.testing_guild_id = testing_guild_id
		self.initial_extensions = initial_extensions
		self.config = config

	async def setup_hook(self):
		for extension in self.initial_extensions:
			await self.load_extension(extension)
			print("🌸", extension, "loaded")

		if self.testing_guild_id:
			guild = discord.Object(self.testing_guild_id)
			self.tree.copy_global_to(guild=guild)
			await self.tree.sync(guild=guild)

		await self.change_presence(
			status=discord.Status.idle,
			activity=discord.Activity(
				type=discord.ActivityType.watching, name="loading up..."
			),
		)

		for guild in self.guilds:
			async with self.db_pool.acquire() as conn:
				try:
					await conn.execute("INSERT INTO servers (id) VALUES ($1) ON CONFLICT DO NOTHING", guild.id)
					if conn.rows_affected:
						print(f"➕ I was added to the guild {guild.name} | {guild.id}, and added it to my database")
				except asyncpg.exceptions.PostgresError as e:
					if "duplicate key value violates unique constraint" in str(e):
						continue
					print(f"🟧 I could not add the guild {guild.name} | {guild.id} to my database:", e)

	async def on_ready(self):
		if not hasattr(self, "uptime"):
			self.uptime = discord.utils.utcnow()

	async def get_or_fetch_user(self, id):
		return self.get_user(id) or await self.fetch_user(id)
	
	async def is_owner(self, user):
		if user.id in self.config['owners']:
			return True
		return False


async def main():
	logger = logging.getLogger("discord")
	logger.setLevel(logging.INFO)

	handler = logging.FileHandler("discord.log", encoding="utf-8")
	handler.setLevel(logging.INFO)

	formatter = logging.Formatter(
		"[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
	)

	handler.setFormatter(formatter)
	logger.addHandler(handler)

	async with ClientSession() as web_client, asyncpg.create_pool(
		user="postgres", password="catness", database="catness-db", command_timeout=30, max_size=10, min_size=5
	) as pool:
		intents = discord.Intents.all()
		prefix = config["prefix"]
		mentions = discord.AllowedMentions(
			roles=False, users=True, everyone=False)
		extensions = ["jishaku", "cogs.events"]
		async with Client(
			db_pool=pool,
			testing_guild_id=904460336118267954,
			web_client=web_client,
			initial_extensions=extensions,
			allowed_mentions=mentions,
			intents=intents,
			command_prefix=prefix,
			config=config
		) as bot:
			await bot.start(config["TOKEN"])

async def shutdown():
	await asyncio.gather(*asyncio.all_tasks())
	loop = asyncio.get_running_loop()
	loop.stop()

async def run():
	try:
		await main()
	except KeyboardInterrupt:
		print("Shutting down...")
	finally:
		await shutdown()

asyncio.run(run())