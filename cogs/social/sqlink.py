import aiosqlite

from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice

from data import Data, DATABASE_FILE

class Link(commands.Cog):
    def __init__(self, ce):
        super().__init__()
        self.ce = ce

    # Define the command to link a social media profile
    @app_commands.command(name="link", description="link your profiles to your discord account")
    @app_commands.choices(platform=[
        Choice(name="LastFM", value="lastfm"),
        Choice(name="Steam", value="steam")
    ])
    async def link(self, interaction, platform:Choice[str], handle:str):
        try:
            user_id = str(interaction.user.id)
            data = await Data.load_db("profiles", user_id)
            if data is None:
                async with aiosqlite.connect(DATABASE_FILE) as conn:
                    await conn.execute(f"INSERT INTO profiles (id) VALUES (?)", (user_id,))
                    await conn.commit()
            async with aiosqlite.connect(DATABASE_FILE) as conn:
                await conn.execute(f"UPDATE profiles SET {platform.value}=? WHERE id=?", (handle, user_id))
                await conn.commit()
            response = f"Linked `{platform.name}` profile: `{handle}`"
        except Exception as e:
            response = e
        await interaction.response.send_message(response, ephemeral=True)

    @app_commands.command(name="unlink", description="Unlink profiles from your account")
    @app_commands.choices(platform=[
        Choice(name="LastFM", value="lastfm"),
        Choice(name="Steam", value="steam"),
        Choice(name="Cake", value="cake")
    ])
    async def unlink(self, interaction, platform:Choice[str]):
        try:
            user_id = interaction.user.id
            async with aiosqlite.connect(DATABASE_FILE) as conn:
                async with conn.execute(f"SELECT {platform.value} FROM profiles WHERE id=?", (user_id,)) as cursor:
                    data = await cursor.fetchone()
                if data is not None and data[0] is not None:
                    await conn.execute(f"UPDATE profiles SET {platform.value} = ? WHERE id = ?", (None, user_id))
                    await conn.commit()
                    response = f"Unlinked your `{platform.name}` profile"
                else:
                    response = f"You have not linked your `{platform.name}` profile. Nothing to unlink."
        except Exception as e:
            response = e
        await interaction.response.send_message(response, ephemeral=True)


async def setup(ce):
    await ce.add_cog(Link(ce))
