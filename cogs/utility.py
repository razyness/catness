import discord
import time
from discord.ext import commands

start_time = time.time()


class Menu(discord.ui.View):

    def __init__(self):
        super().__init__()
        self.value = None


class Utility(commands.Cog):
    def __init__(self, ce):
        self.ce = ce

    @commands.command(brief='View bot\'s status', description='View info about the running instance of the bot. I don\'t know what i\'m saying', aliases=['uptime', 'up'])
    async def status(self, ctx):

        timeUp = time.time() - start_time
        hours = timeUp / 3600
        minutes = (timeUp / 60) % 60
        seconds = timeUp % 60

        users = 0
        channel = 0
        for guild in self.ce.guilds:
            users += len(guild.members)
            channel += len(guild.channels)

        cmdcount = 0
        for command in self.ce.commands:
            cmdcount += 1

        embed = discord.Embed(title=self.ce.user.name + '#' + self.ce.user.discriminator)
        embed.set_thumbnail(url=self.ce.user.avatar.url)
        embed.add_field(name='Owner', value='`Razyness#4486`', inline=True)
        embed.add_field(name='Uptime', value='`{0:.0f} hours, {1:.0f} minutes und {2:.0f} seconds`'.format(hours, minutes, seconds), inline=True)
        embed.add_field(name='Total users', value=f'`{users}`', inline=True)
        embed.add_field(name='Total channels', value=f'`{channel}`', inline=True)
        embed.add_field(name='Bot version', value='`0.6.0`', inline=True)
        embed.add_field(name='Discord.py Version', value=f'`{discord.__version__}`', inline=True)
        embed.add_field(name='Commands count', value=f'`{cmdcount}`', inline=True)
        await ctx.reply(embed=embed)

    @commands.command(brief='View bot\'s latency', description='View bot\'s latency')
    async def ping(self, ctx):
        before = time.monotonic()
        message = await ctx.reply("Pinging...")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"Pong! `{int(ping)} ms`")

    @commands.command(aliases=['av', 'pfp'])
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        view = Menu()
        view.add_item(discord.ui.Button(label='Download', style=discord.ButtonStyle.link, url=member.avatar.url,
                                        emoji='<:download:1004734791553396816>'))

        embed = discord.Embed()
        embed.set_author(name=f'{str(member)}', icon_url=member.avatar.url)
        embed.set_image(url=member.avatar.url)
        await ctx.reply(embed=embed, view=view)


async def setup(ce):
    await ce.add_cog(Utility(ce))
