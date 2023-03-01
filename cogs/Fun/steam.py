from discord import app_commands
from discord.ext import commands
from discord import ui

import discord
import sqlite3
import aiohttp
import toml

config = toml.load("config.toml")
STEAM = config["STEAM"]

conn = sqlite3.connect("profiles.db")

async def load_social_data():
	cursor = conn.cursor()
	cursor.execute("SELECT user_id, lastfm, steam FROM profiles")
	rows = cursor.fetchall()
	social_data = {}
	for row in rows:
		user_id, lastfm, steam = row
		social_data[user_id] = {"lastfm": lastfm, "steam": steam}
	return social_data

class steamProfile(ui.View):
    def __init__(self, user):
        super().__init__()
        self.value = None
        self.user = user


async def getID(user):
    ResolveVanity = f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={STEAM}&vanityurl={user}"
    async with aiohttp.ClientSession() as session:
        async with session.get(ResolveVanity) as response:
            userID = await response.json()
            if userID["response"]["success"] == 1:
                return userID["response"]["steamid"]
        return user


async def mainPage(user):
    userID = await getID(user)
    userID = userID

    PlayerSummaries = f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={STEAM}&steamids={userID}"
    PlayerLevel = f"https://api.steampowered.com/IPlayerService/GetSteamLevel/v1/?key={STEAM}&steamid={userID}"
    async with aiohttp.ClientSession() as session:
        async with session.get(PlayerSummaries) as response:
            userInfo = await response.json()
        async with session.get(PlayerLevel) as response:
            userLevel = await response.json()
    userInfo = userInfo["response"]["players"][0]
    embed = discord.Embed(description=f"`{user}` is level `{userLevel['response']['player_level']}`")
    embed.add_field(name="Member since", value="<t:1640450437:R>")
    name = "Status"
    statuscolor = 0x66c0f4

    if userInfo["personastate"] == 1: 
        lastseen = "`Online`"
        statuscolor = 0x2cc956
    elif userInfo["personastate"] == 0:
        name = "Last seen"
        lastseen = f'<t:{userInfo["lastlogoff"]}:R>'
    elif userInfo["personastate"] == 2:
        lastseen = "`Busy`"
        statuscolor = 0xc92c2c
    elif userInfo["personastate"] == 3:
        lastseen = "`Away`"
        statuscolor = 0xdeaf2c
    elif userInfo["personastate"] == 4:
        lastseen = "`Snooze`"
        statuscolor = 0x223c7d
    else:
        lastseen = "`Hidden/Unavailable`"

    embed.add_field(name=name, value=lastseen)
    if "gameextrainfo" in userInfo:
        embed.add_field(name="In a game", value=f"[{userInfo['gameextrainfo']}](https://store.steampowered.com/app/{userInfo['gameid']})", inline=False)

    embed.title = userInfo["personaname"]
    embed.url = userInfo["profileurl"]
    embed.color = statuscolor
    embed.set_thumbnail(url=userInfo["avatarfull"])
    return embed


class Steam(commands.Cog):

    def __init__(self, ce):
        super().__init__()
        self.ce = ce

    @app_commands.command(name="steam", description="View steam profiles :)")
    @app_commands.describe(user="The user's vanity, steam id or discord mention if they linked their account",
                           ephemeral="Whether the result will be visible to you (True) or everyone else (False)")
    async def steam(self, interaction, user:str=None, ephemeral:bool=True):
        if user is None or user.startswith("<@"):
            if user is None:
                user_id = interaction.user.id
                g = "You"
            elif user.startswith("<@"):
                user_id = int(user[2:-1])
                g = "They"
                if user_id == interaction.user.id:
                    g = "You"
            try:
                data = await load_social_data()
                if str(user_id) in data and "steam" in data[str(user_id)]:
                    if data[str(user_id)]["steam"] is not None:
                        user = data[str(user_id)]["steam"]
                    else:
                        raise Exception
                else:
                    raise Exception
            except:
                await interaction.response.send_message(f"{g} haven't linked your `Steam` account! Run /link to do so", ephemeral=True)
                return
        try:
            embed = await mainPage(user)
            await interaction.response.send_message(embed=embed, ephemeral=ephemeral)
        except Exception as e:
            await interaction.response.send_message(f"I couldn't find the user. Did you use the vanity url of the user? | `{e}`", ephemeral=True)


async def setup(ce):
    await ce.add_cog(Steam(ce))
