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
    from playground import Client

start_time = time.time()


class Events(commands.Cog):
    def __init__(self, bot: Client):
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

    @commands.Cog.listener("on_message")
    @commands.cooldown(1, 5.0, commands.BucketType.user)
    async def oh_thing(self, message):
        if re.search('\boh\b(?!\w)', message.content):
            await message.channel.send("oh")

    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        if message.author.bot:
            return

        if message.content == f"<@!{self.bot.user.id}>":
            await message.channel.send(f"Hello, my prefix is `{self.bot.config['prefix']}`")

        color_hex = re.search('#(([0-9a-fA-F]{2}){3}|([0-9a-fA-F]){3})$', message.content)
        if color_hex:
            color_hex = color_hex.group()
            color_hex = color_hex[1:]
            async with self.bot.web_client.get(f"https://api.color.pizza/v1/{color_hex}") as r:
                data = await r.json()
                await message.add_reaction('🎨')
                await message.channel.typing()
                embed = discord.Embed(title=data["paletteTitle"], color=int(data['colors'][0]['hex'][1:], 16))
                embed.set_thumbnail(
                    url=f"https://dummyimage.com/100x70/{color_hex}/{color_hex}.png")
                fields = [
                    ("Hex", f"`{data['colors'][0]['hex']}`", False),
                    ("RGB", f"`{data['colors'][0]['rgb']['r']}`, `{data['colors'][0]['rgb']['g']}`, `{data['colors'][0]['rgb']['b']}`", False),
                    ("HSL",
                     f"`{round(data['colors'][0]['hsl']['h'], 2)}`, `{round(data['colors'][0]['hsl']['s'], 2)}`, `{round(data['colors'][0]['hsl']['l'], 2)}`", False)
                ]
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                embed.set_footer(text=f"Provided by color.pizza and dummyimage.com")
                await message.reply(embed=embed, delete_after=60.0)



async def setup(bot):
    await bot.add_cog(Events(bot))
