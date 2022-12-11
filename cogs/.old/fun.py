import discord
import time
import random
import pytube
import binascii
import os

from discord import app_commands
from discord.ext import commands

mp4path = 'cache/mp4dl'
mp3path = 'cache/mp3dl'

class Menu(discord.ui.View):

	def __init__(self):
		super().__init__()
		self.value = None


class Fun(commands.Cog):

	def __init__(self, ce):
		self.ce = ce


#    @app_commands.command()
#    async def shouldi(self, ctx, *, decision='do this'):
#
#        responses = ["As I see it, yes.", "Ask again later.", "Better not tell you now.", "Cannot predict now.",
#                     "Concentrate and ask again.",
#                     "Don’t count on it.", "It is certain.", "It is decidedly so.", "Most likely.", "My reply is no.",
#                     "My sources say no.",
#                     "Outlook not so good.", "Outlook good.", "Reply hazy, try again.", "Signs point to yes.",
#                     "Very doubtful.", "Without a doubt.",
#                     "Yes.", "Yes – definitely.", "You may rely on it."]
#        idk = ['idk', 'i don\'t know']
#
#        if decision != 'do this':
#            decision = f'`{decision}`'
#
#        await ctx.send(f'Are you sure you want to {decision}? yes / no / i don\'t know')
#
#        def check(m):
#            return m.author == ctx.author and m.channel == ctx.channel
#
#        conf = await self.ce.wait_for('message', check=check)
#
#        if conf.content.lower() == 'yes':
#            await ctx.reply('Always reflect on your decisions!')
#
#        elif conf.content.lower() in idk:
#            picking = await ctx.reply('Let me pick for you...')
#            time.sleep(2)
#            await picking.edit(content=random.choice(responses))
#
#        else:
#            await ctx.reply('Got it.')

		

async def setup(ce):
	await ce.add_cog(Fun(ce))
