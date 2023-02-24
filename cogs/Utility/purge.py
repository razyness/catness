import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta

# WIP

class Mod(commands.Cog):
    def __init__(self, ce):
        self.ce = ce

    @commands.command(brief='Bulk delete messages',
                      description='Deletes a chosen amount of messages from chat, in bulk. Cannot delete messages '
                                  'older than 2 weeks!',
                      aliases=["clear", "purge"])
    @commands.has_permissions(administrator=True)
    async def clean(self, ctx, limit: int = 5, member: discord.User = None):

        await ctx.message.delete()
        msg = []
        try:
            limit = int(limit)
        except:
            return await ctx.send(f"`{limit}` is not a number")
        if not member:
            await ctx.channel.purge(limit=limit)
            return await ctx.send(f"Deleted `{limit}` messages", delete_after=5)

        async for m in ctx.channel.history():

            if len(msg) == limit:
                break
            if m.author == member and m.created_at < 1209600:
                msg.append(m)

        await ctx.channel.delete_messages(msg)
        await ctx.send(f"Deleted `{limit}` messages by `{str(member)}`", delete_after=5)


async def setup(ce):
    await ce.add_cog(Mod(ce))
