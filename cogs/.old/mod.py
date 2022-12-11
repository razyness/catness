import discord
from discord.ext import commands
from discord import app_commands
from datetime import timedelta
import datetime
import time


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

######### SEEMS LIKE WE NO LONGER NEED THOSE #########

#    @app_commands.command(name='softban', description="Give users a role that doesn't allow them to talkness")
#    @app_commands.checks.has_permissions(administrator=True)
#    async def oldmute(self, interaction, member: discord.Member, *, reason:str='Unspecified'):
#        if member.id == interaction.user.id:
#            await interaction.response.send_message("You cannot mute yourself", ephemeral=True)
#            return
#
#        guild = interaction.guild
#        mutedRole = discord.utils.get(interaction.guild.roles, name="soft banned")
#
#        if not mutedRole:
#            mutedRole = await interaction.guild.create_role(name="soft banned")
#
#            for channel in guild.channels:
#                await channel.set_permissions(mutedRole, speak=False, send_messages=False, read_message_history=False,
#                                              read_messages=False)
#
#        await member.add_roles(mutedRole, reason=reason)
#        embed = discord.Embed(title=f'soft banned `{member}` for `{reason}`')
#        await interaction.response.send_message(embed=embed)
#        dmbed = discord.Embed(
#            title=f"You were soft banned in `{interaction.guild.name}` for `{reason}`.\nDM a staff/owner if you feel this is "
#                  f"unjustified")
#        await member.send(embed=dmbed)
#
#    @app_commands.command(name='unsoftban', description="Unmute to talking")
#    @app_commands.checks.bot_has_permissions(administrator=True)
#    async def oldunmute(self, interaction, member: discord.Member):
#        mutedRole = discord.utils.get(interaction.guild.roles, name="soft banned")
#
#        await member.remove_roles(mutedRole)
#        embed = discord.Embed(title=f'un-softbanned `{member}`')
#        await interaction.response.send_message(embed=embed, delete_after=10)
#        dmbed = discord.Embed(title=f"You were un-softbanned in `{interaction.guild.name}`")
#        await member.send(embed=dmbed)
#
#    @commands.command(brief='Kick users', description='Kicks an user from the guild')
#    @commands.has_permissions(administrator=True)
#    async def kick(self, ctx, Member: discord.Member, *, reason='Unspecified'):
#        if Member.top_role >= ctx.author.top_role:
#            await ctx.send(f"You can only kick members below your top role")
#            return
#        elif Member.top_role >= self.ce.top_role:
#            await ctx.send(f"I can only kick members below my top role")
#            return
#
#        await Member.kick(reason=f'{reason} | Kicked by  {str(ctx.author)}')
#        await ctx.message.delete()
#        await ctx.send(f'Kicked `{str(Member)}` for: `{reason}`', delete_after=5)
#
#    @commands.command()
#    @commands.has_permissions(administrator=True)
#    async def ban(self, ctx, Member: discord.Member, *, reason='Unspecified'):
#        await ctx.message.add_reaction('⏳')
#        if ctx.Member.top_role >= ctx.author.top_role:
#            await ctx.message.clear_reactions()
#            await ctx.message.add_reaction('❌')
#            await ctx.send(f"You can only ban members below your top role")
#            return
#
#        await ctx.message.add_reaction('⏳')
#        await ctx.Member.ban(reason=f'{reason} | Banned by  {str(ctx.author)}')
#        await ctx.message.delete()
#        await ctx.send(f'Banned `{str(Member)}` for: `{reason}`', delete_after=5)
#
#    @commands.command()
#    @commands.has_permissions(administrator=True)
#    async def unban(self, ctx, Member: int):
#        guild = ctx.guild
#        await guild.unban(member=Member)
#        await ctx.message.delete()
#        await ctx.send(f'Unbanned `{str(Member)}`', delete_after=5)
#
#    @commands.command(aliases=['timeout'])
#    @commands.has_permissions(administrator=True)
#    async def mute(self, ctx, Member: discord.Member, mute_time=10, *, reason='Unspecified'):
#        days = mute_time / 1440
#        leftover_minutes = mute_time % 1440
#        hours = leftover_minutes / 60
#        mins = leftover_minutes % 60
#
#        if mute_time > 20160:
#            await ctx.reply(f'could not time out `{Member}`\n`{mute_time} minutes lasts longer than 14 days`')
#            return
#
#        remaining = f'{int(mins)} minutes'
#        if int(hours) > 0:
#            remaining = f'{int(hours)} hours and {remaining}'
#        if int(days) > 0:
#            remaining = f'{int(days)} days, {remaining}'
#
#        await Member.timeout(timedelta(minutes=int(mute_time)), reason=reason)
#        await ctx.message.delete()
#        await ctx.send(f'Timed out `{str(Member)}` for `{remaining}`, for `{reason}`')

######### SEEMS LIKE WE NO LONGER NEED THOSE #########

async def setup(ce):
    await ce.add_cog(Mod(ce))
