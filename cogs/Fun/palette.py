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
    # Fetch the image from the URL
    response = await asyncio.to_thread(requests.get, image_url)
    image_bytes = io.BytesIO(response.content)

    # Load the image
    image = Image.open(image_bytes)

    # Extract colors using colorgram.py library
    colors = await asyncio.to_thread(colorgram.extract, image, palette_size)

    # Adjust palette size to be even
    palette_size = palette_size + (palette_size % 2)

    # Get the actual number of colors extracted
    num_colors = len(colors)

    # Calculate the number of rows and columns based on the actual number of colors
    rows = math.ceil(math.sqrt(num_colors)) - 1
    cols = math.ceil(num_colors / rows)

    # Calculate the dimensions of the color palette image
    palette_width = 50 * cols
    palette_height = 50 * rows

    # Create a new image for the color palette
    palette_image = Image.new('RGB', (palette_width, palette_height))
    draw = ImageDraw.Draw(palette_image)

    # Draw each color in the palette
    x_offset = 0
    y_offset = 0
    for index, color in enumerate(colors):
        if index >= palette_size:
            break  # No need to draw more rectangles if we've reached the palette size limit

        rgb = color.rgb
        draw.rectangle([(x_offset, y_offset), (x_offset + 50, y_offset + 50)], fill=rgb)
        x_offset += 50
        if x_offset >= palette_width:
            x_offset = 0
            y_offset += 50

    # Get bytes of the color palette image
    palette_bytes = io.BytesIO()
    palette_image.save(palette_bytes, format='PNG')
    palette_bytes.seek(0)

    return palette_bytes.getvalue()

class Palette(commands.Cog):
    def __init__(self, ce):
        self.ce = ce

    @app_commands.command(name="palette", description="Generate a color palette from someone's avatar")
    @app_commands.describe(user = "Yes", size="Number of colors to generate. Converted to even +1")
    async def palette(self, inter, user:discord.User=None, size:int=6):
        user = user or inter.user
        if size > 30:
            size = 30
        if size <= 0:
            size = 6
        await inter.response.defer(thinking=True)
        palette_image_bytes = await generate_color_palette(user.avatar.url.replace('1024', '512'), size)
        img = discord.File(io.BytesIO(palette_image_bytes), filename='palette.png')
        await inter.followup.send(content=f"{user.mention}'s palette", file=img)

async def setup(ce):
    await ce.add_cog(Palette(ce))
