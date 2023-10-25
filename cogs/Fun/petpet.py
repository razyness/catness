import discord

from discord.ext import commands
from discord import app_commands

from io import BytesIO
from petpetgif import petpet as petpetgif

class PetPet(commands.Cog):
    """Pet your friends (or foes)"""
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="petpet", description="Create a petpet gif")
    async def pet(self, inter, user: discord.User, server_avatar:bool=True):
        try:
            if server_avatar:
                image = await user.display_avatar.read()
            else:
                image = await user.avatar.read()
        except:
            await inter.response.send_message('You can only mention a member to pet pet pet pet pet pet', ephemeral=True)
            return

        source = BytesIO(image)
        dest = BytesIO()
        petpetgif.make(source, dest)
        dest.seek(0)
        await inter.response.send_message(file=discord.File(dest, filename=f"{image[0]}-petpet.gif"))

async def setup(bot):
    await bot.add_cog(PetPet(bot))