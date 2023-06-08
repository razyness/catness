import aiohttp
import random
import discord

from discord.ext import commands
from discord import app_commands

from data import Data as data

welcome_messages = [
    "Welcome, [username]! Get comfy and enjoy the company!",
    "Hey there, [username]! We've been waiting for you. Let's have some fun!",
    "Welcome aboard, [username]! Prepare for an adventure of a lifetime!",
    "Greetings, [username]! Grab a virtual snack and join the party!",
    "Buckle up, [username]! The excitement starts now!",
    "Welcome, [username]! Get ready to meet fantastic people!",
    "Hey, [username]! This server is all about good vibes and great times!",
    "Step right in, [username]! The fun train is about to depart!",
    "Welcome, [username]! Brace yourself for epic moments!",
    "Hey there, [username]! Prepare to be blown away by our awesome community!",
    "Welcome, [username]! Let's dive into the sea of endless conversations!",
    "Hey, [username]! We've saved you a spot in the laughter zone!",
    "Greetings, [username]! Your presence makes this server even more awesome!",
    "Welcome, [username]! Embrace the chaos and enjoy the ride!",
    "Hey there, [username]! Your arrival just made this server 10 times cooler!",
    "Welcome, [username]! You've joined a family of fantastic individuals!",
    "Welcome, [username]! Prepare to have your socks knocked off!",
    "Hey there, [username]! We're thrilled to have you join our community!",
    "Welcome aboard, [username]! Get ready for a wild ride filled with laughter!",
    "Greetings, [username]! You've just stepped into a realm of endless possibilities!",
    "Buckle up, [username]! Adventure awaits you in every corner of this server!",
    "Welcome, [username]! We're here to make memories and have a great time together!",
    "Hey, [username]! The party starts now. Let's create some unforgettable moments!",
    "Step right in, [username]! Prepare to be amazed by the incredible people here!",
    "Welcome, [username]! Get ready for a community that feels like home!",
    "Hey there, [username]! We're a bunch of friendly folks ready to welcome you with open arms!"
]

class Welcomer(commands.Cog):
    def __init__(self, ce: commands.Bot):
        self.ce = ce

    @commands.Cog.listener("on_member_join")
    async def welcomer(self, member):
        server_data = await data.load_db(table="servers", id=str(member.guild.id), columns=["welcomer"])
        if server_data["welcomer"] == 0:
            return

        patterns = ["general", "main", "chat"]
        channel = next((channel for channel in member.guild.text_channels if any(name.lower() in channel.name.lower() for name in patterns)), None)
        
        if channel:
            print(random.choice(welcome_messages).replace("[username]", member.mention))
            print(channel)
            await channel.send(random.choice(welcome_messages).replace("[username]", member.mention))

async def setup(ce: commands.Bot):
    await ce.add_cog(Welcomer(ce))
