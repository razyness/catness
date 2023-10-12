import discord
import json

from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice


class Link(commands.Cog):
    def __init__(self, bot) -> None:
        super().__init__()
        self.bot = bot

    @app_commands.command(name="link", description='Link your profiles to your discord account')
    @app_commands.choices(platform=[
        Choice(name="LastFM", value="lastfm"),
        Choice(name="Steam", value="steam")
    ])
    async def link(self, inter, platform: Choice[str], handle: str):
        user = inter.user

        async with self.bot.db_pool.acquire() as conn:
            try:
                socials = await conn.fetchval("SELECT socials FROM profiles WHERE id = $1", user.id)
                if socials is None:
                    socials = {}
                else:
                    socials = json.loads(socials)

                if platform.value in socials:
                    if socials[platform.value] == handle:
                        return

                socials[platform.value] = handle
                await conn.execute(
                    "INSERT INTO profiles (id, socials) VALUES ($1, $2) ON CONFLICT (id) DO UPDATE SET socials = $2",
                    user.id,
                    json.dumps(socials)
                )
            except Exception as e:
                await inter.response.send_message(f"An error occurred while linking your profile: {e}", ephemeral=True)
                return

        await inter.response.send_message(f"Linked `{platform.name}` profile: `{handle}`", ephemeral=True)

    @app_commands.command(name="unlink", description="Unlink profiles from your account")
    @app_commands.choices(platform=[
        Choice(name="LastFM", value="lastfm"),
        Choice(name="Steam", value="steam"),
        Choice(name="Cake", value="cake")
    ])
    async def unlink(self, inter, platform: Choice[str]):
        user = inter.user
        async with self.bot.db_pool.acquire() as conn:
            socials = await conn.fetchval("SELECT socials, cake FROM profiles WHERE id = $1", user.id)
            if socials == '{}' and platform.value != 'cake':
                await inter.response.send_message(f"You don't have any socials linked", ephemeral=True)
                return

            socials = json.loads(socials)
            if platform.value not in socials and platform.value != 'cake':
                await inter.response.send_message(f"You don't have your `{platform.name}` linked", ephemeral=True)
                return

            if platform.value == 'cake':
                await conn.execute(
                    "UPDATE profiles SET cake = NULL WHERE id = $1",
                    user.id
                )
                await inter.response.send_message(f"I have removed your birthday forever", ephemeral=True)
            else:
                del socials[platform.value]
                await conn.execute(
                    "UPDATE profiles SET socials = $1 WHERE id = $2",
                    json.dumps(socials),
                    user.id
                )
                await inter.response.send_message(f"I have removed `{platform.name}` from your linked socials", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Link(bot))
