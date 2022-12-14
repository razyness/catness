import discord
import time

from discord.ext import commands
from discord import app_commands

start_time = time.time()


class Status(commands.Cog):
    def __init__(self, ce: commands.Bot):
        self.ce = ce

    @app_commands.command(name='status', description='View info about the running instance of the bot. I '
                                                     'don\'t know what i\'m saying')
    async def status(self, interaction):

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
        for _ in self.ce.commands:
            cmdcount += 1

        embed = discord.Embed(title=str(self.ce.user))
        embed.set_thumbnail(url=self.ce.user.avatar.url)
        embed.add_field(name='Owner', value=f'`{self.ce.owner_id}`', inline=True)
        embed.add_field(name='Uptime',
                        value='`{0:.0f} hours, {1:.0f} minutes and {2:.0f} seconds`'.format(
                            hours, minutes, seconds),
                        inline=True)
        embed.add_field(name='Total users', value=f'`{users}`', inline=True)
        embed.add_field(name='Total channels',
                        value=f'`{channel}`', inline=True)
        embed.add_field(name='Bot version', value='`0.6.0`', inline=True)
        embed.add_field(name='Discord.py Version',
                        value=f'`{discord.__version__}`', inline=True)
        embed.add_field(name='Commands count',
                        value=f'`{cmdcount}`', inline=True)
        await interaction.response.send_message(embed=embed)


async def setup(ce: commands.Bot):
    await ce.add_cog(Status(ce))
