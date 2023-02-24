import discord
from discord.ext import commands
from discord import app_commands


class DownloadButton(discord.ui.View):

	def __init__(self):
		super().__init__()
		self.value = None


class Avatar(commands.Cog):
	def __init__(self, ce:commands.Bot):
		self.ce = ce

	@app_commands.command(name='avatar', description='Get yours/someone\'s avatar')
	@app_commands.describe(member='user hello person avatar')
	async def avatar(self, interaction, member: discord.Member = None):
		member = member or interaction.user

		view = DownloadButton()
		view.add_item(discord.ui.Button(label='Download', style=discord.ButtonStyle.link, url=member.avatar.url,
										emoji='<:download:1062784992243105813>'))

		embed = discord.Embed()
		embed.set_author(name=f'{str(member)}', icon_url=member.avatar.url)
		embed.set_image(url=member.avatar.url)
		await interaction.response.send_message(embed=embed, view=view)


async def setup(ce):
	await ce.add_cog(Avatar(ce))