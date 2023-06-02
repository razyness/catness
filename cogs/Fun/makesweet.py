import discord
import aiohttp
import io, os

from utils.http import HTTP
from typing import Optional
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

from data import config

api_key = config['MAKESWEET']

async def to_bytes(image_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(image_url) as response:
            if response.status == 200:
                return await response.content.read()

async def make_gif(template, text=None, image=None, text_first=False):
    image_bytes = await to_bytes(image.url)
    url = f"https://api.makesweet.com/make/{template}"

    headers = {
        "Authorization": api_key
    }

    data = aiohttp.FormData()

    if text:
        url = url + f'?text={text}'

    if image:
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
        await inter.response.defer(thinking=True)
        gif = await make_gif(template, text, image, swap)
        if gif is None:
            raise Exception("No gif was returned")

        await inter.followup.send(file=discord.File(gif, f"{template}.gif"))

async def setup(ce):
    await ce.add_cog(Makesweet(ce))