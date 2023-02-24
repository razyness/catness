from discord import app_commands
from discord.ext import commands
from discord import ui
import discord
import requests
import toml

config = toml.load("config.toml")
LASTFM = config["LASTFM"]


def playingStatus(user):

    embed = discord.Embed()
    userInfo = f'https://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={user}&api_key={LASTFM}&format=json'
    nowPlaying = f'https://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={user}&api_key={LASTFM}&format=json'
    try:
        r = requests.get(nowPlaying)
        now_playing = r.json()
        r1 = requests.get(userInfo)
        user_data = r1.json()
        if user_data["user"]["subscriber"] == "1":
            embed.set_author(name=f'🔹 ·  {user_data["user"]["name"]}',
                             icon_url=user_data["user"]["image"][2]["#text"],
                             url=user_data["user"]["url"])
            footer_thing = ' · 🔹 is a premium subscriber'
        else:
            embed.set_author(name=f'{user_data["user"]["name"]}',
                             icon_url=user_data["user"]["image"][2]["#text"],
                             url=user_data["user"]["url"])
            footer_thing = ''
        embed.set_thumbnail(
            url=now_playing["recenttracks"]["track"][0]["image"][2]["#text"])
        embed.set_footer(
            text=f'{user_data["user"]["name"]} has {user_data["user"]["playcount"]} scrobbles {footer_thing}')
        status = None
        for i in now_playing["recenttracks"]["track"][0]:
            if i == "@attr":
                status = 'Now Playing'
                break
            elif i == "date":
                status = now_playing["recenttracks"]["track"][0]["date"]["#text"]
                break
        embed.title = f'{now_playing["recenttracks"]["track"][0]["name"]}  ·  {status}'
        embed.url = now_playing["recenttracks"]["track"][0]["url"]
        embed.description = f'by `{now_playing["recenttracks"]["track"][0]["artist"]["#text"]}`\non `{now_playing["recenttracks"]["track"][0]["album"]["#text"]}`'
    except Exception as e:
        embed.add_field(name=f'Something went wrong!',
                        value=f'I failed to collect: {str(e)} | from input: {user}')
    embed.color = 0xe4141e
    return embed


def overview(user):
    embed = discord.Embed()
    userInfo = f'https://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={user}&api_key={LASTFM}&format=json'
    r = requests.get(userInfo)
    user_data = r.json()
    if user_data["user"]["subscriber"] == "1":
        embed.title = f'🔹 ·  {user_data["user"]["realname"]}'
        footer_thing = ' · 🔹 is a premium subscriber'
    else:
        embed.title = f'{user_data["user"]["realname"]}'
        footer_thing = ''
    embed.set_thumbnail(url=user_data["user"]["image"][2]["#text"])
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


def friendsTab(user):

    embed = discord.Embed()
    userInfo = f'https://ws.audioscrobbler.com/2.0/?method=user.getinfo&user={user}&api_key={LASTFM}&format=json'
    friendList = f'http://ws.audioscrobbler.com/2.0/?method=user.getfriends&user={user}&api_key={LASTFM}&format=json'
    r = requests.get(userInfo)
    user_data = r.json()
    r1 = requests.get(friendList)
    friendList = r1.json()
    if user_data["user"]["subscriber"] == "1":
        embed.title = f'🔹 ·  {user_data["user"]["realname"]}'
        footer_thing = ' · 🔹 is a premium subscriber'
    else:
        embed.title = f'{user_data["user"]["realname"]}'
        footer_thing = ''
    embed.set_thumbnail(url=user_data["user"]["image"][2]["#text"])
    embed.set_author(name=f'last.fm - {user_data["user"]["name"]}', url=user_data["user"]["url"],
                     icon_url='https://cdn2.iconfinder.com/data/icons/social-icon-3/512/social_style_3_lastfm-512.png')
    embed.set_footer(
        text=f'{user_data["user"]["name"]} has {user_data["user"]["playcount"]} scrobbles {footer_thing}')
    j = 1
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
                embed.add_field(name=f'🔹· {name}', value=f'{value}')
            else:
                embed.add_field(
                    name=f'{i["name"]}', value=f'{i["realname"]}')
            j += 1
    embed.color = 0xe4141e
    return embed


class fmProfile(ui.View):
    def __init__(self, user, author):
        super().__init__()
        self.value = None
        self.user = user
        self.author = author

    async def disable_all(self):
        for i in self.children:
            i.disabled = True
        await self.msg.edit(view=self)

    async def on_timeout(self):
        await self.disable_all()

    @ui.button(label='Now Playing', style=discord.ButtonStyle.gray)
    async def playing(self, interaction: discord.Integration, button: ui.Button):

        await interaction.response.edit_message(embed=playingStatus(self.user))

    @ui.button(label='Main Menu', style=discord.ButtonStyle.blurple)
    async def main(self, interaction: discord.Interaction, button: ui.Button):

        await interaction.response.edit_message(embed=overview(self.user))

    @ui.button(label='Friends', style=discord.ButtonStyle.gray)
    async def friends(self, interaction, button):

        await interaction.response.edit_message(embed=friendsTab(self.user))

    @ui.button(label='Exit', style=discord.ButtonStyle.red)
    async def quit(self, interaction: discord.Interaction, button: ui.Button):

        await self.disable_all()
        self.value = False
        self.stop()
        await interaction.response.defer()

    async def interaction_check(self, interaction) -> bool:
        if interaction.user.id != self.author:
            await interaction.response.send_message('This is not your menu, run </lastfm:1054381044826112001> to open your own.', ephemeral=True)
            return False
        return True


class LastFM(commands.Cog):

    def __init__(self, ce):
        super().__init__()
        self.ce = ce

    @app_commands.command(name='lastfm', description='Open a lastfm profile menu')
    @app_commands.describe(user="The unique Last.fm username",
                           ephemeral="Whether the result will be visible to you (True) or everyone else (False)")
    async def lastfm(self, interaction, user: str, ephemeral: bool = False):

        author = interaction.user.id
        view = fmProfile(user, author)
        await interaction.response.send_message(embed=overview(user), view=view, ephemeral=ephemeral)
        view.msg = await interaction.original_response()

async def setup(ce):
    await ce.add_cog(LastFM(ce))
