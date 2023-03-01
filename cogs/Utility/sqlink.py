import sqlite3
from typing import List

from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice


class Link(commands.Cog):
    def __init__(self, ce):
        super().__init__()
        self.ce = ce

        # Connect to the SQLite database
        self.conn = sqlite3.connect('profiles.db')
        self.cur = self.conn.cursor()

        # Create the table if it doesn't exist
        self.cur.execute('''CREATE TABLE IF NOT EXISTS profiles
                            (user_id TEXT, lastfm TEXT, steam TEXT)''')
        self.conn.commit()

    # Define the command to link a social media profile
    @app_commands.command(name="link", description="link your profiles to your discord account")
    @app_commands.choices(platform=[
        Choice(name="LastFM", value="lastfm"),
        Choice(name="Steam", value="steam")
    ])
    async def link(self, interaction, platform:Choice[str], handle:str):
        try:
            user_id = str(interaction.user.id)
            self.cur.execute(f"SELECT * FROM profiles WHERE user_id='{user_id}'")
            result = self.cur.fetchone()
            if result is None:
                self.cur.execute(f"INSERT INTO profiles (user_id) VALUES ('{user_id}')")
                self.conn.commit()
            self.cur.execute(f"UPDATE profiles SET {platform.value}='{handle}' WHERE user_id='{user_id}'")
            self.conn.commit()
            response = f"Linked `{platform.name}` profile: `{handle}`"
        except Exception as e:
            response = e
        await interaction.response.send_message(response, ephemeral=True)

    @app_commands.command(name="unlink", description="Unlink profiles from your account")
    @app_commands.choices(platform=[
        Choice(name="LastFM", value="lastfm"),
        Choice(name="Steam", value="steam")
    ])
    async def unlink(self, interaction, platform:Choice[str]):
        try:
            cursor = self.conn.cursor()
            user_id = interaction.user.id
            cursor.execute(f"SELECT {platform.value} FROM profiles WHERE user_id=?", (user_id,))
            data = cursor.fetchone()
            if data is not None and data[0] is not None:
                cursor.execute(f"UPDATE profiles SET {platform.value} = ? WHERE user_id = ?", (None, user_id))
                self.conn.commit()
                response = f"Unlinked your `{platform.name}` profile"
            else:
                response = f"You have not linked your `{platform.name}` profile. Nothing to unlink."
        except Exception as e:
            response = e
        await interaction.response.send_message(response, ephemeral=True)
    def __del__(self):
        self.conn.close()


async def setup(ce):
    await ce.add_cog(Link(ce))
