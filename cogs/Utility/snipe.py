import discord
import asyncio

from pathlib import Path
from urllib.parse import urlparse

from discord.ext import commands
from discord import app_commands
from datetime import timezone

from utils import Paginator, to_relative

class SnipeData:
    def __init__(self, content, author, message_id, creation_date, attachments, stickers, channel_id):
        self.content = content
        self.author = author
        self.message_id = message_id
        self.creation_date = creation_date
        self.attachments = attachments
        self.stickers = stickers
        self.channel_id = channel_id


class EditSnipeData:
    def __init__(self, before, after, author, message_id, creation_date, jump_url, channel_id):
        self.before = before
        self.after = after
        self.author = author
        self.message_id = message_id
        self.creation_date = creation_date
        self.jump_url = jump_url
        self.channel_id = channel_id


class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.snipe_data = {}
        self.edit_snipe_data = {}

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot or not message.author:
            return

        if message.attachments and [a for a in message.attachments if a.is_voice_message()]:
            return

        channel = message.channel

        snipe_data = SnipeData(
            content=str(message.content),
            author=message.author,
            message_id=message.id,
            creation_date=message.created_at.replace(tzinfo=timezone.utc),
            attachments=message.attachments or [],
            stickers=message.stickers or [],
            channel_id=channel.id
        )
        self.snipe_data[channel.id] = snipe_data

        await asyncio.sleep(120)

        if channel.id in self.snipe_data and message.id == self.snipe_data[channel.id].message_id:
            del self.snipe_data[channel.id]

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or not before.author:
            return

        channel = before.channel
        snipe_data = EditSnipeData(
            before=str(before.content),
            after=str(after.content),
            author=before.author,
            message_id=before.id,
            creation_date=before.created_at.replace(tzinfo=timezone.utc),
            jump_url=before.jump_url,
            channel_id=channel.id
        )
        self.edit_snipe_data[channel.id] = snipe_data

        await asyncio.sleep(120)

        if channel.id in self.edit_snipe_data and before.id == self.edit_snipe_data[channel.id].message_id:
            del self.edit_snipe_data[channel.id]

    @app_commands.command(name='snipe', description='Get the last deleted message in this channel')
    @app_commands.guild_only()
    async def snipe(self, inter):
        channel = inter.channel
        if channel.id not in self.snipe_data:
            await inter.response.send_message('There is nothing to snipe!', ephemeral=True)
            return

        snipe_data = self.snipe_data[channel.id]
        time_ago = to_relative(snipe_data.creation_date.timestamp())
        
        embed = discord.Embed(title=None, description=snipe_data.content)
        embed.set_author(name=f"{snipe_data.author} · {time_ago}",
                         icon_url=snipe_data.author.display_avatar.url)

        if not snipe_data.attachments and not snipe_data.stickers:
            return await inter.response.send_message(embed=embed)

        elif len(snipe_data.attachments) > 1 or (snipe_data.attachments and snipe_data.stickers):
            pages = []
            for page in (snipe_data.attachments + snipe_data.stickers):
                temp = discord.Embed(title=None, description=snipe_data.content)
                temp.set_author(name=f"{snipe_data.author} · {time_ago}",
                         icon_url=snipe_data.author.display_avatar.url)
                temp.set_image(url=page.url)
                if isinstance(page, discord.StickerItem):
                    if page.format == discord.StickerFormatType.lottie:
                        temp.description += f"\nAnimated sticker: {page.name}"
                    elif page.format == discord.StickerFormatType.apng:
                        temp.description += f"\nAnimated sticker: [{page.name}]({page.url})"

                if isinstance(page, discord.Attachment) and Path(urlparse(page.url).path).suffix not in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                    temp.description += f"\nVideo file: [{page.filename}]({page.url})"

                pages.append(temp)

            pager = Paginator(invoke=inter, bot=self.bot, owned=True, pages=pages)
            return await pager.start(ephemeral=False)
        
        elif snipe_data.stickers:
            embed.set_image(url=snipe_data.stickers[0].url)
            if isinstance(snipe_data.stickers[0], discord.StickerItem):
                    if snipe_data.stickers[0].format == discord.StickerFormatType.lottie:
                        embed.description += f"\nAnimated sticker: {snipe_data.stickers[0].name}"
                    elif snipe_data.stickers[0].format == discord.StickerFormatType.apng:
                        embed.description += f"\nAnimated sticker: [{snipe_data.stickers[0].name}]({snipe_data.stickers[0].url})"

        elif len(snipe_data.attachments) == 1:
            embed.set_image(url=snipe_data.attachments[0].url)
            if Path(urlparse(snipe_data.attachments[0].url).path).suffix not in ['.png', '.jpg', '.jpeg', '.gif', 'webp']:
                embed.description += f"\n[{snipe_data.attachments[0].filename}]({snipe_data.attachments[0].url})"

        await inter.response.send_message(embed=embed)

    @app_commands.command(name='editsnipe', description='Get the last edited message in this channel')
    @app_commands.guild_only()
    async def editsnipe(self, inter):
        channel = inter.channel
        if channel.id not in self.edit_snipe_data:
            await inter.response.send_message('There is nothing to snipe!', ephemeral=True)
            return

        snipe_data = self.edit_snipe_data[channel.id]
        time_ago = to_relative(snipe_data.creation_date.timestamp())
        

        embed = discord.Embed(title=None, description=snipe_data.before)
        embed.set_author(name=f"{snipe_data.author} · {time_ago}",
                         icon_url=snipe_data.author.display_avatar.url,
                         url=snipe_data.jump_url)

        await inter.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Snipe(bot))
