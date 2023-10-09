import discord
from discord import app_commands
from discord.ext import commands
import time

class errorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.tree.on_error = self.on_tree_error

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
            retry_after = error.retry_after + time.time()
            message = f"Command on cooldown! Try again <t:{int(retry_after)}:R>"

        elif isinstance(error, app_commands.MissingPermissions):
            message = f"You're missing permissions to use that"
        elif isinstance(error, app_commands.AppCommandError):
            message = f"oopsie detected - `{error}"
        else:
            raise Exception

        try:
            return await interaction.response.send_message(message, ephemeral=True)
        except:
            return await interaction.followup.send(message, ephemeral=True)

async def setup(bot):
    await bot.add_cog(errorHandler(bot))
