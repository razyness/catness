import discord
from discord.ext import commands
from discord import app_commands

from utils import icons


class Menu(discord.ui.View):

	def __init__(self):
		super().__init__()
		self.value = None


class Spotify(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(name='spotify', description='View the user\'s spotify activity')
	@app_commands.guild_only()
	@app_commands.describe(member='The activity user')
	async def spotify(self, interaction, member: discord.Member = None):

		if not member:
			member = interaction.guild.get_member(interaction.user.id)

		song = discord.utils.find(lambda a: isinstance(
			a, discord.Spotify), member.activities)

		if song is None:
			await interaction.response.send_message(f'`{member.global_name}` is not playing a song', ephemeral=True)
			return

		else:
			view = Menu()
			view.add_item(discord.ui.Button(label='Play on Spotify', style=discord.ButtonStyle.link,
											url=f'https://open.spotify.com/track/{song.track_id}',
											emoji=icons.spotify_white))
			embed = discord.Embed(title=f'**{song.title}**',
								  description=f'by `{song.artist.replace(";", ",")}`\non `{song.album}`')
			embed.set_thumbnail(url=song.album_cover_url)
			embed.set_footer(text=f'track id: {song.track_id}')
			embed.set_author(
				name=f'{member.display_name}  •  Now Playing', icon_url=member.display_avatar.url)
			await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
	await bot.add_cog(Spotify(bot))
