from discord import app_commands
from discord.ext import commands
from sakana import TENOR
import requests
import random


class Tenor(commands.Cog):
    def __init__(self, ce):
        super().__init__()
        self.ce = ce

    @app_commands.command(name="catgif", description="Random Tenor cat gif")
    async def tenor(self, interaction):
        # set the apikey and limit
        apikey = TENOR  # click to set to your apikey
        lmt = 50
        # set the client_key for the integration and use the same value for all API calls
        ckey = "tenor-api"

        variations=["cats", "kitten gif", "small cat", "cute cat", "loafed cat", "cat jumping", "kitten playing", "the cats", "a cat", "a kitten walking"]

        query = random.choice(variations).replace(" ", "+")

        # get the top 8 GIFs for the search term
        r = requests.get(
            f"https://tenor.googleapis.com/v2/search?q={query}&key={apikey}&client_key={ckey}&limit={lmt}&random=true")

        result = r.json()

        result = result["results"][0]["itemurl"]

        await interaction.response.send_message(result)


async def setup(ce):
    await ce.add_cog(Tenor(ce))
