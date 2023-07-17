import discord

import asyncio
import asyncpg
import logging

from typing import List, Optional

from discord.ext import commands
from aiohttp import ClientSession

from data import config


class Client(commands.AutoShardedBot):
    def __init__(
        self,
        *args,
        initial_extensions: List[str],
        db_pool: asyncpg.Pool,
        web_client: ClientSession,
        testing_guild_id: Optional[int],
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.db_pool = db_pool
        self.web_client = web_client
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_extensions

    async def setup_hook(self):

        for extension in self.initial_extensions:
            await self.load_extension(extension)
            print("  ", extension, "loaded")

        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    async def on_ready(self):
        if not hasattr(self, 'uptime'):
            self.uptime = discord.utils.utcnow()


async def main():

    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler('discord.log', encoding='utf-8')
    handler.setLevel(logging.INFO)

    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter(
        '[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    async with ClientSession() as web_client, asyncpg.create_pool(user='postgres', password="catness", database="catness-db", command_timeout=30) as pool:

        intents = discord.Intents.all()
        prefix = config["prefix"]
        mentions = discord.AllowedMentions(
            roles=False, users=True, everyone=False)
        extensions = ["jishaku", "cogs.events"]
        async with Client(
            db_pool=pool,
            testing_guild_id=config['testing_guild'],
            web_client=web_client,
            initial_extensions=extensions,
            allowed_mentions=mentions,
            intents=intents,
            command_prefix=prefix
        ) as ce:
            await ce.start(config["TOKEN"])

asyncio.run(main())
