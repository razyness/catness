import discord
from discord.ext import commands

class Events(commands.Cog):
	def __init__(self, ce):
		self.ce = ce
	
	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		
		if isinstance(error, commands.MissingRequiredArgument):
			await ctx.send(error)

	@commands.Cog.listener()
	async def on_ready(self):

		await self.ce.change_presence(activity=discord.Activity(
			type=discord.ActivityType.watching, name="me i'm razyness"))

		print(f"Logged in as {self.ce.user}")


async def setup(ce):
	await ce.add_cog(Events(ce))