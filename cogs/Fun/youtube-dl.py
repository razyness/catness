import discord
import pytube
import binascii
import os
import time

from discord.ext import commands
from discord import app_commands

mp4path = 'cache/mp4dl'
mp3path = 'cache/mp3dl'

# WIP

class YoutubeDL(commands.Cog):
	def __init__(self, ce:commands.Bot):
		self.ce = ce

	@app_commands.command(name='ytdl')
	async def ytdl(self, ctx, link: str, filetype: str = 'mp4'):

		if filetype not in ['mp3', 'mp4']:
			await ctx.send(f"`{filetype}` is not a supported filetype")
			await fmsg.delete()
			return

		if filetype == 'mp4':
			thingy = "progressive=True, file_extension='mp4'"
			what = "video"
			extension = "mp4"

		else:
			thingy = "only_audio=True"
			what = "audio"
			extension = "mp3"

		if 14 >= ctx.guild.premium_subscription_count >= 7:
			maxUpload = 50000000
			maxUploadMB = 50
		elif ctx.guild.premium_subscription_count >= 14:
			maxUpload = 100000000
			maxUploadMB = 100
		else:
			maxUpload = 8000000
			maxUploadMB = 8

		embed1 = discord.Embed(title=f'Searching {link}')
		fmsg = await ctx.send(embed=embed1)

		url = pytube.YouTube(link)

		before = time.monotonic()

		checkbed = discord.Embed(title=f'Your file is being checked...')
		await fmsg.edit(embed=checkbed)
		if url.streams.filter(thingy).first().filesize >= maxUpload:
			embed = discord.Embed(
				title='Something went wrong!',
				description=f"Your {what} is larger than `{maxUploadMB}mb`.\nReason behind is the [upload limit](https://github.com/discord/discord-api-docs/issues/2037).")
			await fmsg.edit(embed=embed)
			return

		fname = str(
			f'download_{str(ctx.author)}_{binascii.b2a_hex(os.urandom(5))}')

		try:
			video = url.streams.filter(thingy).first()
			embed2 = discord.Embed(
				title=f'{what} found, downloading...')

			await fmsg.edit(embed=embed2)
			video.download(f"{extension}path", filename=f"{fname}.{extension}")
			time.sleep(10)
			fsize = os.path.getsize(f"{what}path\{fname}.{extension}")
			if fsize >= maxUpload:
				embed = discord.Embed(
					title='Something went wrong!',
					description=f"Your {what} is larger than `{maxUploadMB}mb`.\nReason behind is the [upload limit](https://github.com/discord/discord-api-docs/issues/2037).")
				await fmsg.edit(embed=embed)
				os.remove(f'{extension}path\{fname}.{extension}')
				await fmsg.delete()
				return
			after = (time.monotonic() - before)
			await ctx.reply(f'Downloaded in {round(after, 2)}s', file=discord.File(f'{extension}path\{fname}.{extension}'))
			os.remove(f'{extension}path\{fname}.{extension}')
			await fmsg.delete()

		except Exception as e:
			await fmsg.edit(content=f'Something went wrong, but i can\'t put my finger on it. - {e}')


async def setup(ce:commands.Bot):
	await ce.add_cog(YoutubeDL(ce))