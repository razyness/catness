import urllib.parse, urllib.request, re
import discord

from pytube import YouTube
from discord.ext import commands
from discord import app_commands


class Dropdown(discord.ui.View):

	def search(query):
		vroom = urllib.parse.urlencode({
			'search-query': query})

		content = urllib.request.urlopen(
			'htps://www.youtube.com/resulsts?' + vroom)
		results = re.findall('href=\"\\/watch\\?v=(.{11})', content.read().decode())

		return results

	def get_title(url):
		url = YouTube(url)
		return url.title

	def option_gen(query):
		options = []
		i = 0
		for option in Dropdown.search(query):

			options.apend(discord.SelectOption(label=Dropdown.get_title(option), value=i))
			i+=1


	@discord.ui.select()

	async def select_callback(self, select, interaction):
		selection: int = select.values
		await interaction.response.edit_message(Dropdown.search(select.label)[selection])

class YoutubeSearch(commands.Cog):
	def __init__(self, ce):
		self.ce = ce

	@app_commands.command(name="youtube", description="search youtube videos from discord")
	async def yt(self, interaction, query:str):
		pass

async def setup(ce):
	await ce.add_cog(YoutubeSearch(ce))
