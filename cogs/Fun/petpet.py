import discord
from discord.ext import commands
from discord import app_commands
from io import BytesIO
from petpetgif import petpet as petpetgif

class PetPet(commands.Cog):
    def __init__(self, ce):
        self.ce = ce

    @app_commands.command(name="petpet", description="Create a petpet gif")
    async def pet(self, inter, user: discord.User):
        try:
            image = await user.avatar.read()

        except:
            await inter.response.send_message('You can only mention a member to pet pet pet pet pet pet', ephemeral=True)
            return

        source = BytesIO(image)
        dest = BytesIO()
        petpetgif.make(source, dest)
        dest.seek(0)
        await inter.response.send_message(file=discord.File(dest, filename=f"{image[0]}-petpet.gif"))

async def setup(ce):
    await ce.add_cog(PetPet(ce))