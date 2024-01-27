from __future__ import annotations

import random
import pathlib
import time

from typing import TYPE_CHECKING

from utils import icons

import discord

from discord.ext import commands, tasks

if TYPE_CHECKING:
    from playground import Client

start_time = time.time()


class Events(commands.Cog):
    def __init__(self, bot: Client):
        self.bot = bot
        self.tree = bot.tree
        self.blocked = ["cogs.events", "cogs.Fun.openapi",
                        'cogs.Fun.manga']
        self.cogs_path = pathlib.Path("cogs")
        self.extensions = [self.format_cog(str(item)) for item in self.cogs_path.glob(
            '**/*.py') if self.format_cog(str(item)) not in self.blocked]

    def format_cog(self, string: str):
        return string.replace("\\", ".")[:-3]

    @tasks.loop(seconds=20.0)
    async def presences(self):
        await self.bot.change_presence(status=discord.Status.online, activity=discord.CustomActivity(
            name=random.choice(self.bot.config["bot_config"]["catchphrases"])))

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.change_presence(status=discord.Status.idle, activity=discord.CustomActivity(
            name='loading up...'))

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

    @commands.Cog.listener("on_guild_join")
    async def on_guild_join(self, guild):

        patterns = ["moderator-only", "staff", "gen", "main", "chat"]
        channel = next((channel for channel in guild.text_channels if any(
            name.lower() in channel.name.lower() for name in patterns)), None)

        if channel:
            embed = discord.Embed(title="Thanks for adding me!!",
                                  description="I'm a bot that can do a lot of random things.\nCheck out a full list of commands with `/help`!\n## Quickstart:")

            embed.add_field(name="🔨 Tweak your settings",
                            value="You and your server can opt out of global levels, on-message features and more in your settings.")
            embed.add_field(name="🔗 Integrate with me",
                           value="You can link your `steam` and `lastfm`, and add your birthday with `/link` and `/cake`.")
            embed.set_thumbnail(url=self.bot.user.avatar.url)
            embed.set_footer(
                text="Join my server @ discord.gg/invitelink | We're always open to suggestions!")
            view = discord.ui.View()

            view.add_item(discord.ui.Button(emoji="<:grinning:1153096096558612481>", label="Invite me!",
                          url=f"https://discord.com/api/oauth2/authorize?client_id={self.bot.user.id}&permissions=8&scope=bot%20applications.commands", style=discord.ButtonStyle.url))

            await channel.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Events(bot))
