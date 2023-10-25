from discord import app_commands
from discord.ext import commands

import discord
import time
import asyncpg


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
        elif isinstance(error, asyncpg.exceptions.PostgresError):
            await ctx.send("There was an error with the database. Please try again later.")

    async def on_tree_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            retry_after = error.retry_after + time.time()
            message = f"Command on cooldown! Try again <t:{int(retry_after)}:R>"

        elif isinstance(error, app_commands.MissingPermissions):
            message = f"You're missing permissions to use that"

        elif isinstance(error, app_commands.AppCommandError):
            message = f"oopsie detected - `{error}"

        elif isinstance(error, asyncpg.exceptions.PostgresError):
            message = "There was an error with the database. Please try again later."

        else:
            raise Exception

        try:
            return await interaction.response.send_message(message, ephemeral=True)
        except:
            return await interaction.followup.send(message, ephemeral=True)


async def setup(bot):
    await bot.add_cog(errorHandler(bot))
