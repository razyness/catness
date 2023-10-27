from __future__ import annotations

import random
import pathlib
import time
import asyncpg
import re

from typing import TYPE_CHECKING

import discord

from discord.ext import commands, tasks

if TYPE_CHECKING:
    from playground import Bot

start_time = time.time()

last_executed = 0


def assert_cooldown():
    global last_executed
    if last_executed + 5.0 < time.time():
        last_executed = time.time()
        return True
    return False


class Events(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.tree = bot.tree
        self.blocked = ["cogs.events", "cogs.fun.openapi",
                        'cogs.fun.manga']
        self.cogs_path = pathlib.Path("cogs")
        self.extensions = [self.format_cog(str(item)) for item in self.cogs_path.glob(
            '**/*.py') if self.format_cog(str(item)) not in self.blocked]

    def format_cog(self, string: str):
        return string.replace("\\", ".")[:-3]

    @tasks.loop(seconds=20.0)
    async def presences(self):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Activity(
            type=discord.ActivityType.watching, name=random.choice(self.bot.config["catchphrases"])))

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(status=discord.Status.idle, activity=discord.Activity(
            type=discord.ActivityType.watching, name='loading up...'))

        for extension in self.extensions:
            try:
                await self.bot.load_extension(extension)
                print(f'   {extension} was loaded')
            except Exception as e:
                print(f'🟥 {extension} was not loaded: {e}')

        try:
            synced = await self.bot.tree.sync()
            print(f"🔁 synced {len(synced)} slash commands")
        except Exception as e:
            print(e)

        print(
            f"🟩 Logged in as {self.bot.user} with a {round(self.bot.latency * 1000)}ms delay")

        if not self.presences.is_running():
            self.presences.start()

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        async with self.bot.db_pool.acquire() as conn:
            try:
                await conn.execute("INSERT INTO servers (id) VALUES ($1)", guild.id)
                print(
                    f"📥 I have joined the guild {guild.name} | {guild.id}, and added it to my database")
            except asyncpg.exceptions.PostgresError as e:
                print(
                    f"🟥 I could not add the guild {guild.name} | {guild.id} to my database:", e)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        async with self.bot.db_pool.acquire() as conn:
            try:
                await conn.execute("DELETE FROM servers WHERE id = $1", guild.id)
                print(
                    f"📤 I have left the guild {guild.name} | {guild.id}, and removed it from my database")
            except asyncpg.exceptions.PostgresError as e:
                print(
                    f"🟥 I could not remove the guild {guild.name} | {guild.id} from my database:", e)

    @commands.Cog.listener()
    async def on_message(self, message):

        if self.bot.user in message.mentions:
            await message.channel.send(f"My prefix is `{self.bot.command_prefix}`, but you can also use `/slash` commands", delete_after=10)

        if assert_cooldown():
            if re.search('\boh\b(?!\w)', message.content):
                await message.channel.send("oh")


async def setup(bot):
    await bot.add_cog(Events(bot))
