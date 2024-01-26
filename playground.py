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

    def reload_config(self):
        """
        Returns:
            dict[str]: contents of the updated config file
        """
        self.config = toml.load("./config.toml")
        return self.config

    async def setup_hook(self):
        for extension in self.initial_extensions:
            await self.load_extension(extension)
            print("🌸", extension, "loaded")

        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            self.tree.copy_global_to(guild=guild)
            try:
                await self.tree.sync(guild=guild)
            except:
                pass

        await self.change_presence(
            status=discord.Status.idle,
            activity=discord.Activity(
                type=discord.ActivityType.watching, name="loading up..."
            ),
        )

    async def on_ready(self):
        if not hasattr(self, "uptime"):
            self.uptime = discord.utils.utcnow()

    # hi lizness
    async def get_or_fetch_user(self, id):
        return self.get_user(id) or await self.fetch_user(id)

    async def is_owner(self, user):
        if user.id in self.config["ids"]["owners"]:
            return True

        return await super().is_owner(user)

    async def close(self):
        await super().close()
        await self.db_pool.close()
        await self.web_client.close()


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

    connection = config["db_config"]

    async with ClientSession() as web_client, asyncpg.create_pool(
            user=connection["user"],
            password=connection["password"],
            database=connection["database"],
            command_timeout=connection["command_timeout"],
            max_size=connection["max_size"],
            min_size=connection["min_size"]
    ) as pool:
        intents = discord.Intents.all()
        prefix = config["bot_config"]["prefix"]
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
            try:
                await bot.start(config["keys"]["TOKEN"])
            finally:
                await bot.close()


async def shutdown():
    tasks = [task for task in asyncio.all_tasks() if task is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)

    loop = asyncio.get_running_loop()
    await loop.shutdown_asyncgens()
    loop.stop()


async def run():
    try:
        await main()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        await shutdown()


asyncio.run(run())
