import discord
import aiohttp
import io, os
import moviepy.editor as mp

from utils.http import HTTP
from typing import Optional
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from PIL import Image

from data import config

api_key = config['MAKESWEET']

async def to_bytes(media_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(media_url) as response:
            response.raise_for_status()

            file_object = io.BytesIO(await response.read())

            try:
                image = Image.open(file_object)

                if image.format == 'GIF':
                    image.seek(0)
                    image = image.convert('RGBA')
                    image = image.convert('RGB')
                    image = image.crop((0, 0, image.width, image.height))

                if image.mode == 'RGBA':
                    image = image.convert('RGB')

                aspect_ratio = image.width / image.height
                new_width = 512
                new_height = int(new_width / aspect_ratio)
                image = image.resize((new_width, new_height))

                output_file = io.BytesIO()
                image.save(output_file, format='PNG')

                return output_file.getvalue()
            except:
                return file_object.getvalue()


async def make_gif(template, text=None, image=None, text_first=False):
    url = f"https://api.makesweet.com/make/{template}"

    headers = {
        "Authorization": api_key
    }

    data = aiohttp.FormData()

    if text:
        url = url + f'?text={text}'

    if image:
        image_bytes = await to_bytes(image.url)
        data.add_field(name='images', value=image_bytes, filename=image.filename)

    if text and text_first:
        url = url + f'&textfirst=1'

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=data) as response:
            if response.status == 200:
                r = await response.content.read()
                return io.BytesIO(r)
            else:
                print(f"Request failed with status {response.status}")
                return None

class Makesweet(commands.Cog):
    def __init__(self, ce) -> None:
        super().__init__()
        self.ce = ce
    
    @app_commands.command(name="makesweet", description="Funny heart locked sealed away forever")
    @app_commands.describe(template="For example heart-locket for niko my beloved",
                           image="Will be prioritized to text if only one of them is available",
                           text="Will be passed as second parameter, i.e. right side of heart lockedt",
                           swap="Swap image and text so text comes first")
    @app_commands.choices(template=[
        Choice(name="Heart Locket", value="heart-locket"),
        Choice(name="Flying Bear", value="flying-bear"),
        Choice(name="Flag", value="flag"),
        Choice(name="Billboard City", value="billboard-cityscape"),
        Choice(name="Nesting Doll", value="nesting-doll"),
        Choice(name="Circuit Board", value="circuit-board")
    ])
    async def makesweet(self, inter, template:str, image:discord.Attachment=None, text:str=None, swap:bool=False):
        if os.path.basename(image.url).split('.')[-1] not in ['jpeg', 'jpg', 'gif', 'png', 'webp']:
            return await inter.response.send_message("The only allowed formats are `jpg`, `png`, `gif` and `webp`!!", ephemeral=True)

        await inter.response.defer(thinking=True)
        gif = await make_gif(template, text, image, swap)
        if gif is None:
            raise Exception("No gif was returned")

        await inter.followup.send(file=discord.File(gif, f"{template}.gif"))

async def setup(ce):
    await ce.add_cog(Makesweet(ce))