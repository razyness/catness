from __future__ import annotations

import time

from typing import TYPE_CHECKING

import discord

from discord.ext import commands
from discord import app_commands
from PIL import Image

if TYPE_CHECKING:
    from playground import Bot

start_time = time.time()


class Status(commands.Cog):
    def __init__(self, ce: commands.Bot):
        self.ce = ce

    @app_commands.command(name='about', description='1k subs special FaQ!!! ❤')
    async def status(self, interaction):
        cmds = self.ce.tree.get_commands() or await self.ce.tree.fetch_commands()

        razy = self.ce.get_user(self.ce.owner_id or 592310159133376512) or await self.ce.fetch_user(self.ce.owner_id or 592310159133376512)

        embed = discord.Embed(title=str(self.ce.user))

        if len(self.ce.shards) > 20:
            shard_thing = f"Automatically sharded ~ `{len(self.ce.shards)}/{self.ce.shard_count}`"
        else:
            shard_thing = f"Automatically sharded ~ `{', '.join(str(i) for i in self.ce.shards.keys())}/{self.ce.shard_count}`"

        embed.description = f"""
        Hi i am discord bot for discord and real
        My prefix is `{self.ce.command_prefix}` and i support `/app commands`
        {shard_thing}
        """
        embed.set_thumbnail(url=self.ce.user.display_avatar.url)
        embed.add_field(name='owner', value=f'`{razy}`', inline=True)
        embed.add_field(name='uptime',
                        value=f'<t:{int(start_time)}:R>',
                        inline=True)
        embed.add_field(name='total users',
                        value=f'`{len(self.ce.users)}`', inline=True)
        embed.add_field(name='total guilds',
                        value=f'`{len(self.ce.guilds)}`', inline=True)
        embed.add_field(name='d.py version',
                        value=f'`{discord.__version__}`', inline=True)
        embed.add_field(name='cmd count',
                        value=f'`{len(cmds)}`', inline=True)

        view = discord.ui.View(timeout=None)
        view.add_item(discord.ui.Button(
            label='Invite', style=discord.ButtonStyle.link,
            url="https://discordapp.com/oauth2/authorize?client_id=1029864621047304203&scope=bot+applications.commands&permissions=1099511627775",
            emoji='<:grinning_face_smiling:1109581692819210311>')
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(ce: commands.Bot):
    await ce.add_cog(Status(ce))
