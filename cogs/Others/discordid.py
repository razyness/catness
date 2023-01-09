import requests
from discord import app_commands
from discord.ext import commands
import discord
from sakana import TOKEN
import struct

app = TOKEN


def stamp(snowflake_id):
    snowflake_struct = struct.unpack('>Q', snowflake_id.to_bytes(8, byteorder='big'))[0]
    timestamp = (snowflake_struct >> 22) + 1420070400000
    return int(timestamp / 1000)


statuscodes = [
    '100', '101', '102', '200', '201', '202', '203', '204', '206', '207', '300', '301', '302', '303', '304', '305',
    '307', '308', '400', '401', '402', '403', '404', '405', '406', '407', '408', '409', '410', '411', '412', '413',
    '414', '415', '416', '417', '418', '420', '422', '423', '424', '425', '426', '429', '431', '444', '450', '451',
    '497', '498', '499', '500', '501', '502', '503', '504', '506', '507', '508', '509', '510', '511', '521', '522',
    '523', '525', '599']


class DiscordID(commands.Cog):
    def __init__(self, ce) -> None:
        super().__init__()
        self.ce = ce

    @app_commands.command(name="profile", description="View anyone's profile from their id")
    async def discord_id(self, interaction, userid: str):
        response = requests.get(
            f"https://discord.com/api/v9/users/{userid}", headers={"Authorization": f"Bot {app}"})
        print(response.json())
        if response.status_code == 200:
            try:
                data = response.json()
                embed = discord.Embed(
                    title=f"{data['username']}#{data['discriminator']}",
                    url=f"https://discord.com/users/{userid}")
                ext = "png"
                if data["avatar"].startswith("a_"):
                    ext = "gif"
                embed.set_thumbnail(
                    url=f"https://cdn.discordapp.com/avatars/{userid}/{data['avatar']}.{ext}?size=4096")
                if data["accent_color"] is not None:
                    embed.color = data["accent_color"]
                if data["banner"] is not None:
                    ext = "png"
                    if data["banner"].startswith("a_"):
                        ext = "gif"
                    embed.set_image(url=f"https://cdn.discordapp.com/banners/{userid}/{data['banner']}.{ext}?size=4096")
                embed.add_field(name="Public flags", value=data["public_flags"])
                embed.add_field(name="Creation date", value=f"<t:{stamp(int(userid))}:R>")
                await interaction.response.send_message(embed=embed)
            except Exception as e:
                await interaction.response.send_message(e)
        else:
            await interaction.response.send_message(f"https://http.cat/{response.status_code}.jpg",
                                                    ephemeral=True)


async def setup(ce):
    await ce.add_cog(DiscordID(ce))
