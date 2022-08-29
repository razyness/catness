import discord
import time
from discord.ext import commands


class Mod(commands.Cog):

	def __init__(self, ce):
		self.ce = ce
	
	@commands.command(brief='Bulk delete messages', description='Deletes a chosen amount of messages from chat, in bulk.\n Cannot delete messages older than 2 weeks!', pass_context=True, aliases=["clear", "purge"])
	@commands.has_permissions(administrator=True)
	async def clean(self, ctx, Limit: int):
		await ctx.channel.purge(limit=Limit + 1)
		await ctx.send(f'{ctx.author.mention} purged {Limit} messages', delete_after=5)


async def setup(ce):
	await ce.add_cog(Mod(ce))