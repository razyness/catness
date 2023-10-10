import discord 
import aiohttp, asyncio
import emoji as emj

from discord.ext import commands
from discord import app_commands

from utils.data import icons

root_url = "https://www.gstatic.com/android/keyboard/emojikitchen"

dates = [
  "20201001",
  "20210218",
  "20210521",
  "20210831",
  "20211115",
  "20220110",
  "20220203",
  "20220406",
  "20220506",
  "20220815",
  "20220823",
  "20221101",
  "20221107",
  "20230126",
  "20230301",
  "20230405",
  "20230418",
]

async def to_unicode(emoji):
	try:
		return f"u{hex(ord(emoji.strip()[0]))[2:]}"
	except:
		return False

async def get_emoji_image(session, url):
	async with session.get(url) as response:
		if response.ok:
			return url
	return None

async def get_mix(base, features, session):
	base, features = await to_unicode(base), await to_unicode(features)

	tasks = []
	for date in dates:
		if base != "u1f422":
			url1 = f"{root_url}/{date}/{base}/{base}_{features}.png"
			tasks.append(get_emoji_image(session, url1))

		url2 = f"{root_url}/{date}/{features}/{features}_{base}.png"
		tasks.append(get_emoji_image(session, url2))

	results = await asyncio.gather(*tasks)
	for result in results:
		if result:
			return result

	return False

class Thing(discord.ui.View):
	def __init__(self, image_url):
		super().__init__(timeout=180)
		self.image_url = image_url

	async def disable_all(self, view=None):
		for i in self.children:
			i.disabled = True
		try:
			await self.msg.edit(view=view)
		except:
			return

	async def on_timeout(self):
		await self.disable_all(view=self)
				
	@discord.ui.button(label="Save", emoji=icons.download, style=discord.ButtonStyle.blurple)
	async def view(self, inter, button):
		await inter.response.send_message(self.image_url, ephemeral=True)

class EmojiMix(commands.Cog):
	def __init__(self, bot) -> None:
		super().__init__()
		self.bot = bot
	
	@app_commands.command(name="emojimix", description="Emoji kitchen thingy :3")
	@app_commands.describe(base="The base emojifor the mix",
						   features="What the base should have on it i think")
	async def emoji_mix(self, inter, base:str, features:str):
		if not all(char in emj.EMOJI_DATA for char in base) and not all(char in emj.EMOJI_DATA for char in features):
			return await inter.response.send_message("did you know that inputs must be emojis", ephemeral=True)
				
		image_url = await get_mix(base, features, self.bot.web_client)

		if not image_url:
			return await inter.response.send_message("I couldn't mix those! Try a different pair", ephemeral=True)

		embed = discord.Embed(title=f"Mix of {base} + {features} =")
		embed.set_author(name="Emoji Kitchen")
		embed.set_thumbnail(url=image_url)
		embed.set_footer(icon_url="https://cdn.discordapp.com/emojis/1112740924934594670.gif?size=96", text="Tip: inverting emojis can give different results!!")
		view = Thing(image_url)
		await inter.response.send_message(embed=embed, view=view)
		view.msg = await inter.original_response()

async def setup(bot):
	await bot.add_cog(EmojiMix(bot))
