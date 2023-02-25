import time

from discord.ext import commands
from discord import app_commands


class Ping(commands.Cog):
    def __init__(self, ce: commands.Bot):
        self.ce = ce

    @app_commands.command(name='ping', description='View bot\'s latency')
    async def ping(self, interaction):
        before = time.monotonic()
        await interaction.response.send_message("Pinging...", ephemeral=True)
        ping = (time.monotonic() - before) * 1000
        await interaction.edit_original_response(content=f"Pong! `{int(ping)} ms`")

    @app_commands.command(name="backtopeppino")
    async def peppino(self, interaction):
        await interaction.response.send_message("https://cdn.discordapp.com/attachments/1031621777824174131/1078282294806183996/0sAW181.png")


async def setup(ce: commands.Bot):
    await ce.add_cog(Ping(ce))
