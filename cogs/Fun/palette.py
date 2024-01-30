import discord
import io
import asyncio
import colorgram
import requests
import math

from PIL import Image, ImageDraw
from discord.ext import commands
from discord import app_commands


async def generate_color_palette(image_url, palette_size=10):
	response = await asyncio.to_thread(requests.get, image_url)
	image_bytes = io.BytesIO(response.content)

	image = Image.open(image_bytes)

	colors = await asyncio.to_thread(colorgram.extract, image, palette_size)

	palette_size = palette_size + (palette_size % 2)

	num_colors = len(colors)

	rows = math.ceil(math.sqrt(num_colors)) - 1
	cols = math.ceil(num_colors / rows)

	palette_width = 50 * cols
	palette_height = 50 * rows

	palette_image = Image.new('RGB', (palette_width, palette_height))
	draw = ImageDraw.Draw(palette_image)

	x_offset = 0
	y_offset = 0
	for index, color in enumerate(colors):
		if index >= palette_size:
			break

		rgb = color.rgb
		draw.rectangle(
			[(x_offset, y_offset), (x_offset + 50, y_offset + 50)], fill=rgb)
		x_offset += 50
		if x_offset >= palette_width:
			x_offset = 0
			y_offset += 50

	palette_bytes = io.BytesIO()
	palette_image.save(palette_bytes, format='PNG')
	palette_bytes.seek(0)

	return palette_bytes.getvalue()


class Palette(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name="palette", description="Generate a color palette from someone's avatar")
	@app_commands.describe(user="Yes", size="Number of colors to generate. Converted to even +1")
	async def palette(self, inter, user: discord.User = None, size: int = 8):
		user = user or inter.user
		if size > 30:
			size = 30
		if size <= 1:
			size = 6
		await inter.response.defer(thinking=True)
		palette_image_bytes = await generate_color_palette(user.avatar.url.replace('1024', '512'), size)
		img = discord.File(io.BytesIO(palette_image_bytes),
						   filename='palette.png')
		await inter.followup.send(content=f"{user.mention}'s palette", file=img)


async def setup(bot):
	await bot.add_cog(Palette(bot))
