import discord
from discord.ext import commands
import discord, os, pytube
from discord.ext import commands
import time
import binascii

mp4path = 'cache/mp4dl'
mp3path = 'cache/mp3dl'


class Youtube(commands.Cog):
    def __init__(self, ce):
        self.ce = ce

    @commands.command()
    async def command(self, ctx, link, filetype='mp4'):

        if 14 >= ctx.guild.premium_subscription_count >= 7:
            maxUpload = 50000000
            maxUploadMB = 50
        elif ctx.guild.premium_subscription_count >= 14:
            maxUpload = 100000000
            maxUploadMB = 100
        else:
            maxUpload = 8000000
            maxUploadMB = 8

        async with ctx.typing():
            if filetype is None:
                filetype = 'mp4'

            embed1 = discord.Embed(title=f'Searching {link}')
            fmsg = await ctx.send(embed=embed1)

            url = pytube.YouTube(link)

            fname = str(
                f'download_{str(ctx.author)}_{binascii.b2a_hex(os.urandom(5))}')
            if filetype == 'mp4':
                video = url.streams.filter(
                    progressive=True, file_extension='mp4').first()
                embed2 = discord.Embed(
                    title='Video found, downloading...')
                before = time.monotonic()
                await fmsg.edit(embed=embed2)
                video.download(mp4path, filename=fname + '.mp4')
                time.sleep(10)
                fsize = os.path.getsize(f"{mp4path}\{fname}.mp4")
                if fsize >= maxUpload:
                    embed = discord.Embed(
                        title='Where\'s my video?',
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
                before = time.monotonic()
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
                await ctx.send(f"`{filetype}` is not a supported filetype")
                await fmsg.delete()

    @commands.Cog.listener()
    async def on_message(self, message, link, filetype):
        ctx = await self.ce.get_context(message)
        command = self.ce.get_command('command')
        await ctx.invoke(command, link, filetype, kwarg1=None, kwarg2='mp4')


async def setup(ce):
    await ce.add_cog(Youtube(ce))
