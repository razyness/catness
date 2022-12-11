import discord
import asyncio
from discord import app_commands
from discord.ext import commands

snipe_message_content = ''
snipe_message_author = None
snipe_message_id = None
sn_author_name = None
delete_time = None
creation_date = None
attachment = None


class Snipe(commands.Cog):
	def __init__(self, ce):
		self.ce = ce


	@commands.Cog.listener()
	async def on_message_delete(self, message):

		if message.author.bot:
			return

		global snipe_message
		global snipe_message_author
		global sn_author_name
		global snipe_message_id
		global creation_date
		global attachment

		snipe_message = str(message.content)
		snipe_message_author = message.author.id
		snipe_message_id = message.id
		if message.attachments != []:
			attachment = message.attachments[0]
		sn_author_name = message.author
		creation_date = str(message.created_at)

		await asyncio.sleep(60)

		if message.id == snipe_message_id:
			snipe_message_author = None
			snipe_message = None
			snipe_message_id = None
			sn_author_name = None
			creation_date = None
			attachment = None

	@app_commands.command(name='snipe', description='Get last deleted message')
	async def snipe(self, interaction: discord.Interaction):
		if snipe_message_id is None:
			await interaction.response.send_message('There is nothing to snipe!', ephemeral=True)

		else:
			embed = discord.Embed(title=None, description=f'{snipe_message}')
			embed.set_author(
				name=f"{sn_author_name} · at {creation_date[11:-16]}", icon_url=sn_author_name.avatar.url)

			if attachment != None:
				embed.set_image(url=attachment.url)

			await interaction.response.send_message(embed=embed)
			return


async def setup(ce):
	await ce.add_cog(Snipe(ce))
