from discord.ext import commands
import discord
import os
import pytube
import time
import binascii

mp4path = 'cache/mp4dl'
mp3path = 'cache/mp3dl'


class Youtube(commands.Cog):
    def __init__(self, ce):
        self.ce = ce

    @commands.Cog.listener()
    async def on_message(self, message):
        
        if message.channel.id == 1030920952952930384:

            link = message.content.split()[0]

            if message.author.bot:
                return

            elif 'youtu' not in link:
                await message.delete()
                return
        else:
            return

        maxUpload = 8000000

        await message.add_reaction('⏳')
        url = pytube.YouTube(link)
        fname = str(
            f'download_{str(message.author)}_{binascii.b2a_hex(os.urandom(5))}')

        video = url.streams.filter(
            progressive=True, file_extension='mp4').first()

        before = time.monotonic()

        video.download(mp4path, filename=fname + '.mp4')
        time.sleep(10)

        fsize = os.path.getsize(f"{mp4path}/{fname}.mp4")

        if fsize >= maxUpload:
            await message.clear_reactions()
            await message.add_reaction('❌')
            os.remove(f'{mp4path}/{fname}.mp4')

        after = (time.monotonic() - before)
        await message.channel.send(f'{message.author.mention} Downloaded in `{round(after, 1)}s`', file=discord.File(f'{mp4path}/{fname}.mp4'))
        await message.clear_reactions()
        await message.add_reaction('✅')
        os.remove(f'{mp4path}/{fname}.mp4')



async def setup(ce):
    await ce.add_cog(Youtube(ce))
