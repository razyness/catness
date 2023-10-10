from discord.ext import commands
from discord import app_commands

class Reaction(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name='reaction', description='Live slug reaction')
	async def reaction(self, interaction):
		try:
			r = self.bot.session.get(f"https://tenor.googleapis.com/v2/search?q=live-reaction&key={self.bot.config['TENOR']}&client_key=tenor-api&limit=50&random=true")
			result = await r.json()
			result = result["results"][0]["itemurl"]
			await interaction.response.send_message(result)
		except Exception as e:
			print(e)
	
async def setup(bot):
	await bot.add_cog(Reaction(bot))