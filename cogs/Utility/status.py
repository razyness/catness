from __future__ import annotations

import time
import discord
import psutil, pynvml

import asyncio
from discord.ext import commands
from discord import app_commands

from utils import icons, ui

from utils import Paginator, ButtonMenu

from cogs.Utility.reminder import RemindObject

pynvml.nvmlInit()


class ThingView(ui.View):
	def __init__(self, invoke: discord.Interaction, bot):
		super().__init__(view_inter=invoke)
		self.invoke = invoke
		self.bot = bot
		self._changelog_channel = bot.get_channel(1179908797393817601)

	def format_embed(self, message: discord.Message):
		content = message.content
		title = None
		description = None
		image = None
		footer = None

		parts = content.split("[")
		for part in parts:
			if "title=" in part:
				title = part.split("=")[1].split("]")[0]
			elif "description=" in part:
				description = part.split("=")[1].split("]")[0]
			elif "footer=" in part:
				footer = part.split("=")[1].split("]")[0]
			elif "thumbnail=" in part:
				image = part.split("=")[1].split("]")[0]

		embed = discord.Embed()
		embed.title = title
		embed.description = description
		embed.set_footer(text=f"{message.author.display_name}: {footer}", icon_url=message.author.display_avatar.url)
		embed.timestamp = message.created_at
		embed.set_author(name="Changelog")
		embed.set_thumbnail(url=image)
		return embed

	@discord.ui.button(label='Show changelog', style=discord.ButtonStyle.blurple)
	async def changelog(self, interaction, button):
		pages = []

		async for message in self._changelog_channel.history(limit=50):
			if message.author.id in self.bot.config["ids"]["owners"]:
				pages.append(self.format_embed(message))

		pager = Paginator(interaction, self.bot, pages, wrap=True)
		await pager.start()


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
					gpu_info.append(f"`{gpu_name}`: `{gpu_memory_info.used / (1024 ** 3):.2f}GB` Used")
			else:
				handle = pynvml.nvmlDeviceGetHandleByIndex(0)
				gpu_name = pynvml.nvmlDeviceGetName(handle)
				gpu_memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
				gpu_info = [f"`{gpu_memory_info.used / (1024 ** 3):.2f}GB` Used"]

			embed.add_field(name="Usage",
							value=f"CPU: `{cpu_percent}%` | Mem: `{memory_usage}%` {chr(10)}GPU: {chr(10).join(gpu_info)}")

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

	@app_commands.command(name="vote", description="vote for me on top.gg 😁")
	@app_commands.checks.cooldown(1, 43200, key=lambda i: i.user.id)
	async def vote(self, interaction):

		async def callback(inter):
			task = "Hi!! It is now time for a devious [top.gg vote](https://top.gg/bot/1008875850403414049/vote).\nRun `/vote` if you wish to be reminded again!!"
			remind_obj = RemindObject(inter.user.id, task, int(
				time.time() + 43200), (True, None), "vote-reminder")

			async with self.bot.db_pool.acquire() as conn:
				async with conn.transaction():
					reminders = await conn.fetch("SELECT * FROM reminders WHERE id = $1 AND reminder_id = $2",
												 inter.user.id, "vote-reminder")
					if reminders:
						return await interaction.edit_original_response(
							content="It appears that you have already set a reminder.. How did you even do this?",
							view=None)

					await conn.execute(
						"INSERT INTO reminders (id, task, remind_time, private, channel, reminder_id) VALUES ($1, $2, $3, $4, $5, $6)",
						inter.user.id, task, remind_obj.remind_time, True, str(remind_obj.channel[1]), "vote-reminder")

			await interaction.edit_original_response(content=f"Okay! See you <t:{int(time.time() + 43200)}:R> :heart:",
													 view=None)

		menu = ButtonMenu(interaction, self.bot)
		menu.add_button(callback=callback, label="Yes, please!", style="blurple")
		await interaction.response.send_message(
			"Here's a link: https://top.gg/bot/1008875850403414049/vote\nThanks for voting!! Can i remind you in 12 hours?",
			view=menu, ephemeral=True)


async def setup(bot: commands.Bot):
	await bot.add_cog(Status(bot))
