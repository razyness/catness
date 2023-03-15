import aiohttp
import random
import discord

from discord.ext import commands
from discord import app_commands

UNSPLASH_ACCESS_KEY = "iwWhhVfP_YYKFyW0ZZcU_U4MOK7Kv4bfGaTXqqGPyvI"
SEARCH_QUERY = "bumblebee"

async def search_images():
    # set up the request headers with the access key
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }

    # make a search request to Unsplash for images of leaves
    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(f"https://api.unsplash.com/search/photos?query={SEARCH_QUERY}&per_page=100") as response:
            if response.status != 200:
                print(f"Error: failed to get search results from Unsplash ({response.status})")
                return None
            results = await response.json()
            results = results["results"]
            image_urls = [result["urls"]["regular"] for result in results]
            return image_urls

class Feed(discord.ui.View):
    def __init__(self, *, timeout=180):
        super().__init__(timeout=timeout)

    async def disable_all(self):
        for i in self.children:
            i.disabled = True
        await self.msg.edit(view=self)

    async def on_timeout(self):
        await self.disable_all()

    @discord.ui.button(label="Like",style=discord.ButtonStyle.blurple)
    async def gray_button(self, interaction, button):
        await interaction.response.send_message(content=f"Liked! This image will be used to tune your feed", ephemeral=True)


class Silly(commands.Cog):
    def __init__(self, ce: commands.Bot):
        self.ce = ce

    @app_commands.command(name="backtopeppino")
    async def peppino(self, interaction):
        await interaction.response.send_message("https://cdn.discordapp.com/attachments/1031621777824174131/1078282294806183996/0sAW181.png")

    @app_commands.command(name="bee", description="Get a random image of bees")
    @app_commands.describe(ephemeral="Whether the result will be visible to you (True) or everyone else (False)")
    async def leaves(self, interaction, ephemeral:bool=False):
        stuff = await search_images()
        view = Feed()
        await interaction.response.send_message(random.choice(stuff), ephemeral=ephemeral, view=view)
        view.msg = await interaction.original_response()

async def setup(ce: commands.Bot):
    await ce.add_cog(Silly(ce))
