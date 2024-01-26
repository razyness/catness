from discord import app_commands
from discord.ext import commands
from discord import ui

import utils
import json
import discord

from datetime import datetime
import time

from utils import icons, blocking, to_relative

LASTFM = None

async def playing_status(user, session):

    embed = discord.Embed()
    userInfo = f'https://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={user}&api_key={LASTFM}&format=json'
    nowPlaying = f'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={user}&api_key={LASTFM}&format=json'
    try:
        async with session.get(userInfo) as resp:
            user_data = await resp.json()

        async with session.get(nowPlaying) as resp:
            now_playing = await resp.json()

        if user_data["user"]["subscriber"] == "1":
            embed.set_author(name=f'🔹 •  {user_data["user"]["name"]}',
                             icon_url=user_data["user"]["image"][2]["#text"],
                             url=user_data["user"]["url"])
            footer_thing = ' • 🔹 premium subscriber'
        else:
            embed.set_author(name=f'{user_data["user"]["name"]}',
                             icon_url=user_data["user"]["image"][2]["#text"],
                             url=user_data["user"]["url"])
            footer_thing = ''
        embed.set_footer(
            text=f'{user_data["user"]["name"]} has {user_data["user"]["playcount"]} scrobbles {footer_thing}')
        status = None

        if "error" in now_playing:
            if now_playing["error"] == 17:
                embed.description = f'{user_data["user"]["name"]}\'s recent tracks are set to private.'
            else:
                raise Exception

        else:
            for i in now_playing["recenttracks"]["track"][0]:
                if i == "@attr":
                    status = '  •  Now Playing'
                    break
                elif i == "date":
                    status = ""
                    embed.set_footer(text=f'{embed.footer.text}- {to_relative(now_playing["recenttracks"]["track"][0]["date"]["uts"])}')
                    break
            embed.set_thumbnail(
                url=now_playing["recenttracks"]["track"][0]["image"][2]["#text"])
            embed.title = f'{now_playing["recenttracks"]["track"][0]["name"]}{status}'
            embed.url = now_playing["recenttracks"]["track"][0]["url"]
            embed.description = f'by `{now_playing["recenttracks"]["track"][0]["artist"]["#text"]}`\non `{now_playing["recenttracks"]["track"][0]["album"]["#text"]}`'
    except Exception as e:
        embed.add_field(name=f'Something went wrong!',
                        value=f'`{str(e)}`')
    embed.color = 0xe4141e
    return embed


async def overview(user, session):
    embed = discord.Embed()
    userInfo = f'https://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={user}&api_key={LASTFM}&format=json'
    async with session.get(userInfo) as resp:
        user_data = await resp.json()

    if user_data["user"]["subscriber"] == "1":
        embed.title = f'🔹 •  {user_data["user"]["realname"]}'
        footer_thing = ' • 🔹 premium subscriber'
    else:
        embed.title = f'{user_data["user"]["realname"]}'
        footer_thing = ''
    embed.set_thumbnail(url=user_data["user"]["image"][2]["#text"] or 'https://lastfm.freetls.fastly.net/i/u/avatar170s/818148bf682d429dc215c1705eb27b98.png')
    embed.set_author(name=f'last.fm - {user_data["user"]["name"]}', url=user_data["user"]["url"],
                     icon_url='https://cdn2.iconfinder.com/data/icons/social-icon-3/512/social_style_3_lastfm-512.png')
    embed.set_footer(
        text=f'{user_data["user"]["name"]} has {user_data["user"]["playcount"]} scrobbles {footer_thing}')
    for i in user_data["user"]:
        if i not in ["name", "realname", "playcount", "url", "age", "bootstrap", "image", "subscriber", "type"]:
            if i == "gender" and user_data["user"][i] == "n":
                continue
            if i == "registered":
                value = str(user_data["user"][i]).replace(
                    str(user_data["user"][i]), f'<t:{user_data["user"]["registered"]["unixtime"]}:R>')
            else:
                value = user_data["user"][i]
            i = i.replace('_', ' ').title()
            desc = embed.add_field(name=i, value=value)
            try:
                desc.value.replace(str(
                    user_data["user"]["registered"]), f'<t:{user_data["user"]["registered"]["unixtime"]}:R>')
                if user_data["user"]["gender"] == "n":
                    desc.value.replace(
                        str(user_data["user"]["gender"]), f'None')
            except:
                pass
    embed.color = 0xe4141e
    return embed


async def friends_tab(user, session):

    embed = discord.Embed()
    userInfo = f'https://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={user}&api_key={LASTFM}&format=json'
    friendList = f'http://ws.audioscrobbler.com/2.0/?method=user.getfriends&user={user}&api_key={LASTFM}&format=json'

    async with session.get(userInfo) as resp:
        user_data = await resp.json()

    async with session.get(friendList) as resp:
        friendList = await resp.json()
        
    if user_data["user"]["subscriber"] == "1":
        embed.title = f'🔹 •  {user_data["user"]["realname"]}'
        footer_thing = ' • 🔹 premium subscriber'
    else:
        embed.title = f'{user_data["user"]["realname"]}'
        footer_thing = ''
    embed.set_thumbnail(url=user_data["user"]["image"][2]["#text"] or 'https://lastfm.freetls.fastly.net/i/u/avatar170s/818148bf682d429dc215c1705eb27b98.png')
    embed.set_author(name=f'last.fm - {user_data["user"]["name"]}', url=user_data["user"]["url"],
                     icon_url='https://cdn2.iconfinder.com/data/icons/social-icon-3/512/social_style_3_lastfm-512.png')
    embed.set_footer(
        text=f'{user_data["user"]["name"]} has {user_data["user"]["playcount"]} scrobbles {footer_thing}')
    j = 1

    try:
        friendList["friends"]
    except:
        embed.description = f'{user_data["user"]["name"]} has no friends :('
        embed.color = 0xe4141e
        return embed

    for i in friendList["friends"]["user"]:
        if j < 25:
            if len(i["name"]) > 256:
                name = f'{i["name"][0:175]}...'
            else:
                name = i["name"]
            if len(i["realname"]) > 1024:
                value = f'{i["realname"][0:520]}...'
            else:
                value = i["realname"]
            if i["subscriber"] == "1":
                embed.add_field(
                    name=f'🔹• {i["name"]}', value=f'{i["realname"] if i["realname"] != "" else "*No real name set*"}')
            else:
                embed.add_field(
                    name=f'{i["name"]}', value=f'{i["realname"] if i["realname"] != "" else "*No real name set*"}')
            j += 1
    embed.color = 0xe4141e
    return embed


class fmProfile(utils.ui.View):
    def __init__(self, user, author, session, inter, owned, timeout=180):
        super().__init__(inter, owned)
        self.value = None
        self.user = user
        self.author = author
        self.session = session
        self.timeout = timeout
        self.selection = "Main Menu"

        for child in self.children:
            child.disabled = True if child.label == self.selection else False

    @ui.button(label='Now Playing', style=discord.ButtonStyle.gray)
    async def playing(self, interaction: discord.Integration, button: ui.Button):
        self.selection = button.label
        for child in self.children:
            child.disabled = True if child.label == self.selection else False
        embed = await playing_status(self.user, self.session)
        await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label='Main Menu', style=discord.ButtonStyle.blurple)
    async def main(self, interaction: discord.Interaction, button: ui.Button):
        self.selection = button.label
        for child in self.children:
            child.disabled = True if child.label == self.selection else False
        embed = await overview(self.user, self.session)
        await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(label='Friends', style=discord.ButtonStyle.gray)
    async def friends(self, interaction, button):
        self.selection = button.label
        for child in self.children:
            child.disabled = True if child.label == self.selection else False
        embed = await friends_tab(self.user, self.session)
        await interaction.response.edit_message(embed=embed, view=self)

    @ui.button(emoji=icons.close, style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: ui.Button):
        await interaction.response.edit_message(content="Bye-bye", embed=None, view=None, delete_after=2)


class LastFM(commands.Cog):

    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @app_commands.command(name='lastfm', description='Open a lastfm profile menu')
    @app_commands.describe(user="The user's vanity or discord mention if they linked their account",
                           ephemeral="Whether the result will be visible to you (True) or everyone else (False)")
    async def lastfm(self, interaction, user: str = None, ephemeral: bool = False):
        global LASTFM
        LASTFM = self.bot.config["keys"]["LASTFM"]
        if user is None or user.startswith("<@"):
            if user is None:
                user_id = interaction.user.id
                g = "You haven't"
            elif user.startswith("<@"):
                user_id = int(user[2:-1])
                g = f"<@{user_id}> hasn't"
                if user_id == interaction.user.id:
                    g = "You haven't"

            try:
                async with self.bot.db_pool.acquire() as conn:
                    async with conn.transaction():
                        socials = await conn.fetchval("SELECT socials FROM profiles WHERE id = $1", user_id)
                        socials_dict = await blocking.run(lambda: json.loads(socials))
                        if 'lastfm' in socials_dict:
                            user = socials_dict['lastfm']
                        else:
                            raise Exception
            except Exception as e:
                print(e)
                await interaction.response.send_message(f"{g} linked a `LastFM` account! Run </link:1080264642569441380> to do so", ephemeral=True)
                return

        author = interaction.user.id
        view = fmProfile(user, author, self.bot.web_client, interaction, True)
        embed = await overview(user, self.bot.web_client)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=ephemeral)


async def setup(bot):
    await bot.add_cog(LastFM(bot))
