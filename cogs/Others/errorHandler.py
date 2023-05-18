import discord
from discord import app_commands
from discord.ext import commands


class errorHandler(commands.Cog):
    def __init__(self, ce):
        self.ce = ce
        self.ce.tree.on_error = self.on_tree_error

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(error)
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(error)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(error)
        elif isinstance(error, commands.BadArgument):
            await ctx.send(error)

    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            return await interaction.response.send_message(f"Command is currently on cooldown! Try again in `{error.retry_after:.2f}` seconds!", ephemeral=True)
        elif isinstance(error, app_commands.MissingPermissions):
            return await interaction.response.send_message(f"You're missing permissions to use that", ephemeral=True)
        elif isinstance(error, app_commands.AppCommandError):
            return await interaction.response.send_message(f"oopsie detected - `{error}", ephemeral=True)
        else:
            raise Exception

async def setup(ce):
    await ce.add_cog(errorHandler(ce))
