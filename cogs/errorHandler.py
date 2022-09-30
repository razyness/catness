from discord.ext import commands


class errorHandler(commands.Cog):
    def __init__(self, ce):
        self.ce = ce

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


async def setup(ce):
    await ce.add_cog(errorHandler(ce))
