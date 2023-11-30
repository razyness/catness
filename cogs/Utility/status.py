from __future__ import annotations

import time
import discord
import psutil, pynvml

from discord.ext import commands
from discord import app_commands

from utils import icons, ui

from .changelogs import Changelog

pynvml.nvmlInit()

class ThingView(ui.View):
    def __init__(self, invoke: discord.Interaction, bot):
        super().__init__(view_inter=invoke)
        self.invoke = invoke
        self.bot = bot
    
    @discord.ui.button(label='Show changelog', style=discord.ButtonStyle.blurple)
    async def changelog(self, interaction, button):
        changelog = Changelog(interaction, self.bot)
        await changelog.load_changelogs()

class Status(commands.Cog):
    """
    Commands to get information about the bot.
    """
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @app_commands.command(name='about', description='discord about me embed')
    async def status(self, interaction):
        cmds = self.bot.tree.get_commands() or await self.bot.tree.fetch_commands()

        razy = await self.bot.get_or_fetch_user(self.bot.owner_id or 592310159133376512)

        embed = discord.Embed(title=str(self.bot.user))

        if len(self.bot.shards) > 20:
            shard_thing = f"Automatically sharded ~ `{len(self.bot.shards)}/{self.bot.shard_count}`"
        else:
            shard_thing = f"Automatically sharded ~ `{', '.join(str(i) for i in self.bot.shards.keys())}/{self.bot.shard_count}`"

        embed.description = f"""
Hi i am discord bot for discord and real
My prefix is `{self.bot.command_prefix}` and i support `/app commands`
{shard_thing}
        """
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name='owner', value=f'`{razy}`')
        embed.add_field(name='uptime',
                        value=f'<t:{int(self.bot.uptime.timestamp())}:R>',
                        inline=True)
        embed.add_field(name='total users',
                        value=f'`{len(self.bot.users)}`')
        embed.add_field(name='total guilds',
                        value=f'`{len(self.bot.guilds)}`')
        embed.add_field(name='d.py version',
                        value=f'`{discord.__version__}`')
        embed.add_field(name='cmd count',
                        value=f'`{len(cmds)}`')

        if interaction.user == razy:
            cpu_percent = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent

            gpu_count = pynvml.nvmlDeviceGetCount()
            if gpu_count > 1:
                gpu_info = []
                for i in range(gpu_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    gpu_name = pynvml.nvmlDeviceGetName(handle)
                    gpu_memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    gpu_info.append(f"`{gpu_name}`: `{gpu_memory_info.used / (1024**3):.2f}GB` Used")
            else:
                handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                gpu_name = pynvml.nvmlDeviceGetName(handle)
                gpu_memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                gpu_info = [f"`{gpu_memory_info.used / (1024**3):.2f}GB` Used"]

            embed.add_field(name="Usage", value=f"CPU: `{cpu_percent}%` | Mem: `{memory_usage}%` {chr(10)}GPU: {chr(10).join(gpu_info)}")

        view = ThingView(interaction, self.bot)
        view.add_item(discord.ui.Button(
            label='Invite', style=discord.ButtonStyle.link,
            url="https://discordapp.com/oauth2/authorize?client_id=1029864621047304203&scope=bot+applications.commands&permissions=1099511627775",
            emoji='<:grinning:1153096096558612481>')
        )
        view.add_item(discord.ui.Button(
            label="Source",
            url="https://github.com/razyness/catness",
            emoji=icons.github
        ))
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @app_commands.command(name='ping', description='View bot\'s latency')
    async def ping(self, interaction):
        before = time.monotonic()
        await interaction.response.send_message("Pinging...", ephemeral=True)
        ping = (time.monotonic() - before) * 1000
        await interaction.edit_original_response(content=f"Pong! `{int((ping + self.bot.latency) / 2)} ms`")

async def setup(bot: commands.Bot):
    await bot.add_cog(Status(bot))
