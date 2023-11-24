import discord

from discord import ui
from discord import app_commands
from discord.ext import commands

from discord.ext.commands import DefaultHelpCommand


class HelpDropdown(ui.Select):
    def __init__(self, bot):
        self.bot = bot
        placeholder = "Select a command"
        options = [
            discord.SelectOption(
                label=cog.qualified_name,
                description=cog.description,
                value=cog.qualified_name
            ) for cog_name, cog in bot.cogs.items() if cog_name not in ["Help", "Events", "Jishaku"] and (cog.get_commands() or cog.get_app_commands())
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


class Help(commands.Cog):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    async def cog_unload(self):
        self.bot.help_command = DefaultHelpCommand

    async def cog_load(self):
        self.bot.help_command = None

    @commands.hybrid_command(name="help", description="Shows a command browser")
    async def help(self, ctx):
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

        view = ui.View().add_item(HelpDropdown(self.bot))

        await ctx.defer(ephemeral=True)
        await ctx.author.send(embed=embed, view=view, delete_after=180)
        if ctx.message:
            await ctx.message.add_reaction("✅")


async def setup(bot):
    await bot.add_cog(Help(bot))
