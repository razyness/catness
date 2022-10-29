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

    @app_commands.command(name='errorcat', description='sends http cats from http.cat')
    @app_commands.describe(number = 'The status code')
    async def errorcat(self, interaction, number: str = None):
        if number is None:
            number = random.choice(statuscodes)

        if number not in statuscodes:
            await interaction.response.send_message(f'i could not find `{number}`', ephemeral=True)
            return

        embed = discord.Embed()
        embed.set_image(url=f'https://http.cat/{number}.jpg')
        embed.set_footer(text=f'Type .errorcat [status code] to find the one you\'re looking for')
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name='spotify', description='View the user\'s spotify activity')
    @app_commands.describe(member='The activity user')

    async def spotify(self, interaction, member: discord.Member = None):

        member = interaction.guild.get_member(member) or interaction.guild.get_member(interaction.user.id)

        song = discord.utils.find(lambda a: isinstance(a, discord.Spotify), member.activities)

        if song is None:
            await interaction.response.send_message(f'`{str(member)}` is not playing a song', ephemeral=True)
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
            await interaction.response.send_message(embed=embed, view=view)

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

    @commands.command(aliases=["yt", "ytdownload", "youtube"])
    async def ytdl(self, ctx, link, filetype='mp4'):

        if filetype not in ['mp3', 'mp4']:
            await ctx.send(f"`{filetype}` is not a supported filetype")
            await fmsg.delete()
            return

        if 14 >= ctx.guild.premium_subscription_count >= 7:
            maxUpload = 50000000
            maxUploadMB = 50
        elif ctx.guild.premium_subscription_count >= 14:
            maxUpload = 100000000
            maxUploadMB = 100
        else:
            maxUpload = 8000000
            maxUploadMB = 8

        if filetype is None:
            filetype = 'mp4'

        embed1 = discord.Embed(title=f'Searching {link}')
        fmsg = await ctx.send(embed=embed1)

        url = pytube.YouTube(link)

        before = time.monotonic()

        if filetype == 'mp4':
            checkbed = discord.Embed(title=f'Your file is being checked...')
            await fmsg.edit(embed=checkbed)
            if url.streams.first().filesize >= maxUpload:
                embed = discord.Embed(
                        title='Something went wrong!',
                        description=f"Your video is larger than `{maxUploadMB}mb`.\nReason behind is the [upload limit](https://github.com/discord/discord-api-docs/issues/2037).")
                await fmsg.edit(embed=embed)
                return
        elif filetype == 'mp3':
            checkbed = discord.Embed(title=f'Your file is being checked...')
            await fmsg.edit(embed=checkbed)
            if url.streams.filter(only_audio=True).first().filesize >= maxUpload:
                embed = discord.Embed(
                        title='Something went wrong!',
                        description=f"Your audio is larger than `{maxUploadMB}mb`.\nReason behind is the [upload limit](https://github.com/discord/discord-api-docs/issues/2037).")
                await fmsg.edit(embed=embed)
                return

        fname = str(
            f'download_{str(ctx.author)}_{binascii.b2a_hex(os.urandom(5))}')
        if filetype == 'mp4':
            video = url.streams.filter(
                progressive=True, file_extension='mp4').first()
            embed2 = discord.Embed(
                title='Video found, downloading...')
            
            await fmsg.edit(embed=embed2)
            video.download(mp4path, filename=fname + '.mp4')
            time.sleep(10)
            fsize = os.path.getsize(f"{mp4path}\{fname}.mp4")
            if fsize >= maxUpload:
                embed = discord.Embed(
                    title='Something went wrong!',
                    description=f"Your video is larger than `{maxUploadMB}mb`.\nReason behind is the [upload limit](https://github.com/discord/discord-api-docs/issues/2037).")
                await fmsg.edit(embed=embed)
                os.remove(f'{mp4path}\{fname}.mp4')
                await fmsg.delete()
                return
            after = (time.monotonic() - before)
            await ctx.reply(f'Downloaded in {round(after, 2)}s', file=discord.File(f'{mp4path}\{fname}.mp4'))
            os.remove(f'{mp4path}\{fname}.mp4')
            await fmsg.delete()

        elif filetype == 'mp3':
            video = url.streams.filter(only_audio=True).first()
            embed2 = discord.Embed(
                title='Audio found, downloading...')
            await fmsg.edit(embed=embed2)

            video.download(mp3path, filename=fname + '.mp3')
            fsize = os.path.getsize(f"{mp3path}\{fname}.mp3")
            if fsize >= maxUpload:
                embed = discord.Embed(
                    title='Where\'s my audio?',
                    description=f"Your audio is larger than `{maxUploadMB}mb` (somehow).\nReason behind is the [upload limit](https://github.com/discord/discord-api-docs/issues/2037).")
                await ctx.reply(embed=embed)
                os.remove(f'{mp3path}\{fname}.mp3')
                await fmsg.delete()
                return
            after = (time.monotonic() - before)
            await ctx.reply(f'Downloaded in {round(after, 2)}s', file=discord.File(f'{mp3path}\{fname}.mp3'))
            os.remove(f'{mp3path}\{fname}.mp3')
            await fmsg.delete()
        else:
            await fmsg.edit(content='Something went wrong, but i can\'t put my finger on it')


async def setup(ce):
    await ce.add_cog(Fun(ce))
