import discord
import datetime
import aiohttp

from discord.ext import commands
from discord import app_commands


class ConfirmModal(discord.ui.Modal):
    def __init__(self, *, title: str = "Big bug report modal cool", timeout: float | None = 120, ce) -> None:
        super().__init__(title=title, timeout=timeout)
        self.ce = ce

    short = discord.ui.TextInput(
        style=discord.TextStyle.short,
        label="Describe briefly",
        required=True,
        max_length=100,
        placeholder="<command> says The application did not respond..."
    )

    long = discord.ui.TextInput(
        style=discord.TextStyle.long,
        label="Details / how to reproduce",
        required=True,
        max_length=4000,
        placeholder="When i press x button after y button it fails and like\nFeel free to use codeblocks if needed"
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title=self.short.value, description=self.long.value)
        embed.set_author(name="bug report")
        embed.set_footer(
            text=f"submitted by {str(interaction.user)} | {interaction.user.id}",
            icon_url=interaction.user.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()

        await interaction.response.send_message(f"Thank you!! While you wait, you can join support server real and maybe you can help me figure it out\nhttps://discord.gg/invitelink", ephemeral=True)

        webhook_url = "https://canary.discord.com/api/webhooks/1109946330752745502/6PkPFZ-cgD0SXeaf_3zGf-_RLuVs-bWdn4nzCAYD8u0qTLbO3lFUS1RR_J8rLDz1MfU6"

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(url=webhook_url, session=session)
            await webhook.send(embed=embed)


class Report(commands.Cog):
    def __init__(self, ce: commands.Bot):
        self.ce = ce

    @app_commands.command(name='report', description='Report silly issues and errors please')
    @app_commands.checks.cooldown(1, 86400, key=lambda i: (i.user.id))
    async def report(self, interaction):
        modal = ConfirmModal(ce=self.ce)
        await interaction.response.send_modal(modal)


async def setup(ce: commands.Bot):
    await ce.add_cog(Report(ce))
