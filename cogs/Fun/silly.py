from discord.ext import commands
from discord import app_commands


class Silly(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@app_commands.command(name="backtopeppino")
	async def peppino(self, interaction):
		await interaction.response.send_message(
			"https://cdn.discordapp.com/attachments/1031621777824174131/1078282294806183996/0sAW181.png")

	@app_commands.command(name="woody", description="woody from Neighbours from Hell")
	async def woody(self, inter):
		await inter.response.send_message("https://github.com/razyness/catness/raw/main/media/woody.jpg")


async def setup(bot: commands.Bot):
	await bot.add_cog(Silly(bot))
