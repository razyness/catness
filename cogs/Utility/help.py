from typing import Optional
import discord

from discord import app_commands
from discord.ext import commands

from discord.ext.commands import DefaultHelpCommand

from utils.ui import View


class HelpDropdown(discord.ui.Select):
	def __init__(self, bot):
		self.bot = bot
		placeholder = "Select a command"
		options = [
			discord.SelectOption(
				label=cog.qualified_name,
				description=cog.description,
				value=cog.qualified_name
			) for cog_name, cog in bot.cogs.items() if
			cog_name not in ["Help", "Events", "Jishaku"] and (cog.get_commands() or cog.get_app_commands())
		]

		fallback = [discord.SelectOption(
			label="No options available",
			value="none")]

		super().__init__(placeholder=placeholder, options=options or fallback)

	async def callback(self, interaction: discord.Interaction):
		cog = self.bot.get_cog(self.values[0])
		assert cog is not None

		cmd_list = []
		for i in cog.walk_commands():
			if not i.hidden:
				cmd_list.append(i)

		for i in cog.walk_app_commands():
			cmd_list.append(i)

		embed = discord.Embed()
		embed.title = cog.qualified_name
		embed.description = "### " + (cog.description or "No description.")
		embed.set_footer(text=f"{self.bot.user}",
						 icon_url=self.bot.user.display_avatar.url)

		for cmd in cmd_list:
			cmd_desc = cmd.description or "No description."

			if hasattr(cmd, 'parameters'):
				if cmd.parameters:
					cmd_desc += "```"
					for param in cmd.parameters:
						if not param.required:
							cmd_desc += f"\n[{param.name}]: {param.description}"
						else:
							cmd_desc += f"\n<{param.name}>: {param.description}"
					cmd_desc += "```"

			name = cmd.name
			if hasattr(cmd, 'parent') and cmd.parent:
				name = f'{cmd.parent.name} {cmd.name}'

			if isinstance(cmd, app_commands.Command):
				embed.add_field(name=f"/{name}",
								value=cmd_desc, inline=False)
			elif isinstance(cmd, commands.Command):
				embed.add_field(name=f"#{name}",
								value=cmd_desc, inline=False)

		await interaction.response.send_message(embed=embed, ephemeral=True)


class ThingView(View):
	def __init__(self, invoke, timeout: float | None = 180):
		super().__init__(view_inter=invoke, timeout=timeout)

	@discord.ui.button(label="View on-message commands")
	async def viewthing(self, interaction: discord.Interaction, button: discord.ui.Button, ):
		embed = discord.Embed(title="On-message commands",
							  description="These commands can be used by typing them in chat.")
		for i in {
			"y/n": "include it to your message to make a poll",
			"/#000000": "Get the closest color to a hex code, and preview the color",
			"booster hearts": "reacts with ❤ to all booster messages",
		}.items():
			embed.add_field(name=i[0], value=i[1], inline=True)

		await interaction.response.send_message(embed=embed, ephemeral=True)


class Help(commands.Cog):
	def __init__(self, bot):
		super().__init__()
		self.bot = bot
		self.command_dict = {}

	async def cog_unload(self):
		self.bot.help_command = DefaultHelpCommand

	async def cog_load(self):
		for cog_name, cog in self.bot.cogs.items():
			for command in cog.walk_app_commands():
				self.insert_command(command)
		self.bot.help_command = None

	def insert_command(self, command):
		command_info = {
			"group": isinstance(command, app_commands.commands.Group),
			"name": command.name,
			"description": command.description,
			"params": {},
			"children": {}
		}

		if hasattr(command, 'parameters') and command.parameters:
			for param in command.parameters:
				command_info["params"][param.name] = {
					"required": param.required,
					"description": param.description
				}

		self.command_dict[command.name] = command_info

		if isinstance(command, app_commands.commands.Group):
			for subcommand in command.walk_commands():
				self.insert_subcommand(command, subcommand)

	def insert_subcommand(self, parent_command, subcommand):
		subcommand_info = {
			"name": subcommand.name,
			"parent": parent_command.name,
			"description": subcommand.description,
			"params": {}
		}

		if hasattr(subcommand, 'parameters') and subcommand.parameters:
			for param in subcommand.parameters:
				subcommand_info["params"][param.name] = {
					"required": param.required,
					"description": param.description
				}

		self.command_dict[parent_command.name]["children"][subcommand.name] = subcommand_info

	@commands.hybrid_command(name="help", description="Shows a command browser")
	@app_commands.describe(command="Name of command")
	async def help_cmd(self, ctx, command: str = None):
		if command:
			for cmd in self.command_dict:
				if command != cmd:
					continue

				embed = discord.Embed(title=f"{cmd} info")

				command_info = self.command_dict[cmd]
				cmd_desc = command_info["description"]

				if not command_info["group"]:
					if command_info["params"]:
						cmd_desc += "```"
						for param_name, param_info in command_info["params"].items():
							cmd_desc += f"\n{'[' if not param_info['required'] else '<'}{param_name}{']' if not param_info['required'] else '>'}: {param_info['description']}"
						cmd_desc += "```"

					embed.add_field(name=f"/{command_info['name']}",
									value=cmd_desc, inline=False)

				else:
					for subcommand in command_info["children"].items():
						subcommand = subcommand[1]
						cmd_desc = subcommand["description"]
						if subcommand["params"]:
							cmd_desc += "```"

							for param_name, param_info in subcommand["params"].items():
								cmd_desc += f"\n{'[' if not param_info['required'] else '<'}{param_name}{']' if not param_info['required'] else '>'}: {param_info['description']}"

							cmd_desc += "```"

						embed.add_field(name=f"/{subcommand['parent']} {subcommand['name']}",
										value=cmd_desc, inline=False)

				embed.set_footer(text="[ ] optional, < > required", icon_url=self.bot.user.avatar.url)

				return await ctx.reply(embed=embed, ephemeral=True, delete_after=180)

			return await ctx.message.add_reaction("❌") if ctx.message else None

		description = """
Here's a helpful list of commands you can use!

To learn more about a command, just choose the group from the dropdown menu.
As for parameters, `<>` means it's required, and `[]` means it's optional.
Also, `#` means it's a regular command, and `/` means it's an app command.

Fun fact: placing a / before a color hex will show you the closest color to it!
        """
		embed = discord.Embed(title="Command list",
							  description=description)

		embed.set_footer(text="This message will delete in 3 minutes.",
						 icon_url="https://cdn.discordapp.com/emojis/1112740924934594670.gif?size=96")

		view = ThingView(ctx).add_item(HelpDropdown(self.bot))

		await ctx.defer(ephemeral=True)
		await ctx.author.send(embed=embed, view=view, delete_after=180)
		if ctx.message:
			await ctx.message.add_reaction("✅")


async def setup(bot):
	await bot.add_cog(Help(bot))
