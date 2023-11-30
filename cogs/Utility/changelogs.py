from discord.ext import commands
from discord import app_commands

from utils import ui, icons

import discord

class Changelog(ui.View):
    def __init__(self, invoke: discord.Interaction, bot):
        super().__init__(view_inter=invoke)
        self.invoke = invoke
        self.bot = bot
        self._page = 0
        self._pages = []
        self.original_message = None
        self._changelog_channel: discord.TextChannel = bot.get_channel(1179908797393817601)

    def format_embed(self, message: discord.Message):
        content = message.content
        title = None
        description = None
        image = None
        footer = None

        parts = content.split("[")
        for part in parts:
            if "title=" in part:
                title = part.split("=")[1].split("]")[0]
            elif "description=" in part:
                description = part.split("=")[1].split("]")[0]
            elif "footer=" in part:
                footer = part.split("=")[1].split("]")[0]
            elif "thumbnail=" in part:
                image = part.split("=")[1].split("]")[0]

        embed = discord.Embed()
        embed.title = title
        embed.description = description
        embed.set_footer(text=f"{message.author.display_name}: {footer} - {self._page + 1}/{len(self._pages)}", icon_url=message.author.display_avatar.url)
        embed.timestamp = message.created_at
        embed.set_author(name="Changelog")
        embed.set_thumbnail(url=image)
        return embed

    async def update(self, page):
        if not self.original_message:
            self.original_message = await self.invoke.original_response()

        await self.original_message.edit(embed=self.format_embed(page), view=self)

    @discord.ui.button(emoji=icons.page_left, style=discord.ButtonStyle.blurple)
    async def back(self, interaction, button):
        self._page = self._page - 1 if self._page > 0 else len(self._pages) - 1
        await self.update(self._pages[self._page])
        await interaction.response.defer()
    
    @discord.ui.button(emoji=icons.page_right, style=discord.ButtonStyle.blurple)
    async def forward(self, interaction, button):
        self._page = self._page + 1 if self._page < len(self._pages) - 1 else 0
        await self.update(self._pages[self._page])
        await interaction.response.defer()

    async def load_changelogs(self):
        async for message in self._changelog_channel.history(limit=100):
            if message.author.id in self.bot.config['owners']:
                self._pages.append(message)

        self.original_message = await self.invoke.response.send_message(embed=self.format_embed(self._pages[self._page]), ephemeral=True, view=self)

async def setup(bot):
    return