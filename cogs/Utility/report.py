import discord
import datetime

from discord.ext import commands
from discord import app_commands


class ConfirmModal(discord.ui.Modal):
    def __init__(self, *, title: str = "Big bug report modal cool", timeout: float | None = 120, bot) -> None:
        super().__init__(title=title, timeout=timeout)
        self.bot = bot

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
        min_length=200,
        max_length=4000,
        placeholder="When i press x button after y button it fails and like\nFeel free to use codeblocks if needed"
    )

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(title=self.short.value,
                              description=self.long.value)
        embed.set_author(name="bug report")
        embed.set_footer(
            text=f"submitted by @{str(interaction.user)} | {interaction.user.id}",
            icon_url=interaction.user.avatar.url)
        embed.timestamp = datetime.datetime.utcnow()

        channel = self.bot.config['report_channel']
        channel = self.bot.get_channel(channel) or await self.bot.fetch_channel(channel)

        webhook = await channel.create_webhook(name='bug report')

        await webhook.send(embed=embed)
        await webhook.delete(reason='Sent a bug report')

        await interaction.response.send_message(f"Thank you!! While you wait, you can join support server real and maybe you can help me figure it out if you want\nhttps://discord.gg/invitelink", ephemeral=True)


class Report(commands.Cog):
    """This bot is always being worked on!!
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name='report', description='Report silly issues and errors please')
    @app_commands.checks.cooldown(1, 86400, key=lambda i: (i.user.id))
    async def report(self, interaction):
        modal = ConfirmModal(bot=self.bot)
        await interaction.response.send_modal(modal)


async def setup(bot: commands.Bot):
    await bot.add_cog(Report(bot))
