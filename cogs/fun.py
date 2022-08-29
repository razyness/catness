import discord
import time
import random
import pytube
import binascii
import os
from discord.ext import commands
from pytube import YouTube

mp4path = 'cache/mp4dl'
mp3path = 'cache/mp3dl'

statuscodes = [
    '100', '101', '102', '200', '201', '202', '203', '204', '206', '207', '300', '301', '302', '303', '304', '305',
    '307', '308', '400', '401', '402', '403', '404', '405', '406', '407', '408', '409', '410', '411', '412', '413',
    '414', '415', '416', '417', '418', '420', '422', '423', '424', '425', '426', '429', '431', '444', '450', '451',
    '497', '498', '499', '500', '501', '502', '503', '504', '506', '507', '508', '509', '510', '511', '521', '522',
    '523', '525', '599',
]


class Menu(discord.ui.View):

    def __init__(self):
        super().__init__()
        self.value = None


class Fun(commands.Cog):

    def __init__(self, ce):
        self.ce = ce

    @commands.command(brief='bartholomew :D', description='bartholomew :D')
    async def bartholomew(self, ctx):
        thing = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        await ctx.message.delete()
        await thing.reply(
            'https://cdn.discordapp.com/attachments/841451660059869194/1008905457978585088/MemeFeedBot.gif')

    @commands.command(brief='HTTP cats', description='sends http cats from http.cat')
    async def errorcat(self, ctx, number: str = None):
        if number is None:
            number = random.choice(statuscodes)

        if number not in statuscodes:
            await ctx.reply(f'`{number}` is not a valid status code')
            return

        embed = discord.Embed()
        embed.set_image(url=f'https://http.cat/{number}.jpg')
        embed.set_footer(text=f'Type .errorcat [status code] to find the one you\'re looking for')
        await ctx.reply(embed=embed)

    @commands.command(brief='Spotify activity', description='View the user\'s spotify activity', aliases=['s'])
    async def spotify(self, ctx, member: discord.Member = None):

        member = member or ctx.author

        song = discord.utils.find(lambda a: isinstance(a, discord.Spotify), member.activities)

        if song is None:
            await ctx.send(f'`{member.name}#{member.discriminator}` is not playing a song')
            return

        else:
            view = Menu()
            view.add_item(discord.ui.Button(label='Play on Spotify', style=discord.ButtonStyle.link,
                                            url=f'https://open.spotify.com/track/{song.track_id}',
                                            emoji='<:spotify_white:1004734925884370944>'))
            embed = discord.Embed(title=f'**{song.title}**',
                                  description=f'by `{song.artist.replace(";", ",")}`\non `{song.album}`')
            embed.set_thumbnail(url=song.album_cover_url)
            embed.set_footer(text=f'track id: {song.track_id}')
            embed.set_author(name=f'Now playing - {member.display_name}', icon_url=member.avatar.url)
            await ctx.reply(embed=embed, view=view)


async def setup(ce):
    await ce.add_cog(Fun(ce))
