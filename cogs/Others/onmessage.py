from discord.ext import commands
from discord import app_commands

import discord
import re
import time

class OnMessageCmds(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		self.last_executed = time.time()
	
	def assert_cooldown(self):
		if self.last_executed + 4.0 < time.time():
			self.last_executed = time.time()
			return True
		return False

	@commands.Cog.listener("on_message")
	async def hi(self, message):
		if message.author.bot or not message.guild:
			return

		features = await self.bot.db_pool.fetchval("SELECT features FROM servers WHERE id = $1", message.guild.id)

		if not features:
			return

		color_hex = re.search(
			'(?<!<)/#(?:([0-9a-fA-F]{2}){3}|([0-9a-fA-F]){3})(?!\S|>)', message.content)
		if color_hex:
			color_hex = color_hex.group()
			color_hex = color_hex[2:]
			async with self.bot.web_client.get(f"https://api.color.pizza/v1/{color_hex}") as r:
				data = await r.json()
				await message.add_reaction('🎨')
				await message.channel.typing()
				embed = discord.Embed(
					title=data["paletteTitle"], color=int(color_hex, 16))
				if f"#{color_hex}" != str(data["colors"][0]["hex"]):
					embed.title = f"#{color_hex}"
					embed.description = f"**Closest color:** `{data['colors'][0]['name']}`"
				if len(color_hex) != 6:
					embed.colour = discord.Colour(
						int(data['colors'][0]['hex'][1:], 16))
				embed.set_thumbnail(
					url=f"https://dummyimage.com/100x70/{color_hex}/{color_hex}.png")
				fields = [
					("Hex", f"`{data['colors'][0]['hex']}`", False),
					("RGB", f"`{data['colors'][0]['rgb']['r']}`, `{data['colors'][0]['rgb']['g']}`, `{data['colors'][0]['rgb']['b']}`", False),
					("HSL",
					 f"`{round(data['colors'][0]['hsl']['h'], 2)}`, `{round(data['colors'][0]['hsl']['s'], 2)}`, `{round(data['colors'][0]['hsl']['l'], 2)}`", False)
				]
				for name, value, inline in fields:
					embed.add_field(name=name, value=value, inline=inline)
				embed.set_footer(
					text=f"Provided by color.pizza and dummyimage.com")
				await message.reply(embed=embed, delete_after=120.0)

		if "MessageType.premium_guild" in str(message.type):
			await message.add_reaction("❤")

		if re.search(r'\by/n\b', message.content.lower()):
			[await message.add_reaction(i) for i in ["👍", "👎"]]

		# Add cooldown affected events past this
		if not self.assert_cooldown():
			return

		if re.search(r'\boh\b', message.content.lower()):
			await message.channel.send("oh")

async def setup(bot) -> None:
	await bot.add_cog(OnMessageCmds(bot))