from typing import Optional
from discord import ui
from discord.ext import commands
from discord import app_commands

import random
import discord
import itertools

from data import config, Data
from utils.http import HTTP


http = HTTP()


async def get_random_song(lastfm_user):
    url = f"https://ws.audioscrobbler.com/2.0/?method=user.gettoptracks&user={lastfm_user}&api_key={config['LASTFM']}&period=1month&format=json"
    json = await http.get(url=url)
    song_data = json['toptracks']['tracks'][random.randint(
        1, json['toptracks']['tracks'][-1])]
    return song_data


class MixView(ui.View):
    def __init__(self, ce, mix_owner, guests, timeout: float | None = 180):
        super().__init__(timeout=timeout)
        self.ce = ce
        self.mix_owner = mix_owner
        self.guests = guests
        self.failed = []

    async def mix_embed(self):
        embed = discord.Embed(title="The mix in question")
        embed.description = f"A mix of {', '.join(self.guests)} and {self.mix_owner}"
        for i, _ in itertools.product(await self.ce.fetch_user[self.guests], range(4)):
            data = await Data.load_db(table="profiles", user_id=i.id)

            if data is None:
                self.failed.append(i.id)
                continue
            elif data is not None and i.id in self.failed:
                self.failed.remove(i.id)

            song = await get_random_song(data['lastfm'])
            embed.add_field(
                name=f"{song['name']}", value=f"By `{song['artist']['name']}`\nFrom {i.mention}")
        embed.set_footer("Press reroll to make a new one!!")
        return embed

    async def menu(self):
        embed = discord.Embed(title="The mixes are real")
        embed.description = "Invite up to 5 people to your mix but i don't know how yet"
        return embed


class Mix(commands.Cog):
    def __init__(self, ce: commands.Bot):
        self.ce = ce

    @app_commands.command(name="mix", description="Experiment")
    async def mix(self, inter, users: str):
        experiment = await Data.load_db(table="settings", user_id=inter.user.id)
        if experiment['experiments'] != 1:
            return await inter.response.send_message(f"This feature is experimental, enable experiments in your settings to try it out!!", ephemeral=True)

        view = MixView(ce=self.ce, mix_owner=inter.user, guests=users)
        embed = await view.mix_embed()
        await inter.response.send_message(embed=embed)


async def setup(ce: commands.Bot):
    await ce.add_cog(Mix(ce))
