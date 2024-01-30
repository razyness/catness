import discord
import random

from discord import app_commands
from discord.ext import commands

statuscodes = [
	'100', '101', '102', '200', '201', '202', '203', '204', '206', '207', '300', '301', '302', '303', '304', '305',
	'307', '308', '400', '401', '402', '403', '404', '405', '406', '407', '408', '409', '410', '411', '412', '413',
	'414', '415', '416', '417', '418', '420', '422', '423', '424', '425', '426', '429', '431', '444', '450', '451',
	'497', '498', '499', '500', '501', '502', '503', '504', '506', '507', '508', '509', '510', '511', '521', '522',
	'523', '525', '599']


class ErrorCat(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name='errorcat', description='sends http cats from http.cat')
	@app_commands.describe(number='The status code')
	async def errorcat(self, interaction, number: str = None):
		if number is None:
			number = random.choice(statuscodes)

		if number not in statuscodes:
			await interaction.response.send_message(f'i could not find `{number}`', ephemeral=True)
			return

		embed = discord.Embed()
		embed.set_image(url=f'https://http.cat/{number}.jpg')
		embed.set_footer(
			text=f'Type /errorcat [status code] to find the one you\'re looking for')
		await interaction.response.send_message(embed=embed)


async def setup(bot):
	await bot.add_cog(ErrorCat(bot))
