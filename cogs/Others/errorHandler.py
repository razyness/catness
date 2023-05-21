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
            retry_after = error.retry_after
            if retry_after >= 3600:
                hours = int(retry_after // 3600)
                minutes = int((retry_after % 3600) // 60)
                seconds = int((retry_after % 3600) % 60)
                cooldown_message = f"Cooldown! Try again in `{hours}h {minutes}m {seconds}s`"
            elif retry_after >= 60:
                minutes = int(retry_after // 60)
                seconds = int(retry_after % 60)
                cooldown_message = f"Tick tock! Try again in `{minutes}m {seconds}s`"
            else:
                cooldown_message = f"Command on cooldown! Try again in `{retry_after:.2f}s`"

            return await interaction.response.send_message(cooldown_message, ephemeral=True)
        elif isinstance(error, app_commands.MissingPermissions):
            return await interaction.response.send_message(f"You're missing permissions to use that", ephemeral=True)
        elif isinstance(error, app_commands.AppCommandError):
            return await interaction.response.send_message(f"oopsie detected - `{error}", ephemeral=True)
        else:
            raise Exception

async def setup(ce):
    await ce.add_cog(errorHandler(ce))
