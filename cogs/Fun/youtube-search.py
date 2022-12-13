import urllib.parse
import urllib.request
import re
import discord

from pytube import YouTube
from discord.ext import commands
from discord import app_commands
from discord.ui import Select, View


def search(query):
    query = query.replace(' ', '+')
    html = urllib.request.urlopen(
        f"https://www.youtube.com/results?search_query={query}")

    results = re.findall(r"watch\?v=(\S{11})", html.read().decode())

    results = [i for n, i in enumerate(results) if i not in results[:n]]
    print(results)
    return results


def option_gen(query):
    options = []
    i = 1
    options = search(query)

    for option in search(query):
        options.append(discord.SelectOption(
            label=str(YouTube(f'https://www.youtube.com/watch?v={option}').title), value=i, description=f'https://www.youtube.com/?watch={option}', emoji='<:youtube:1051528374574661682>'))
        i += 1
    return options


class Dropdown(View):
    def __init__(self, query):
        super().__init__()
        self.query: str = query

    @discord.ui.select(placeholder='Choose your fighter!', options=[
        discord.SelectOption(label='Razyness', value="1", description="ness")
    ])
    async def select_callback(self, select, interaction):

        # self.options = option_gen(self.query)
        if select.values[0] == "1":
            content = "mrrp meow"
            # view=search(select.label)[selection]
            await interaction.response.edit_message(content=content)

        # placeholder = search(select.label)[selection]
        # discord.ui.select(placeholder, options=option_gen(self.query))
        # content = f'https://www.youtube.com/?watch={search(self.query)[selection]}'


class YoutubeSearch(commands.Cog):
    def __init__(self, ce):
        self.ce = ce

    @app_commands.command(name="youtube", description="search youtube videos from discord")
    async def yt(self, interaction, query: str):
        try:
            content = f'https://www.youtube.com/watch?v={search(query)[0]}'
            view = Dropdown(query)
            await interaction.response.send_message(content, view=view)
        except Exception as e:
            await interaction.response.send_message(e)


async def setup(ce):
    await ce.add_cog(YoutubeSearch(ce))
