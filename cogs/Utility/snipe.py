import discord
import asyncio

from discord.ext import commands
from discord import app_commands

class SnipeData:
    def __init__(self, content, author, message_id, creation_date, attachment, channel_id):
        self.content = content
        self.author = author
        self.message_id = message_id
        self.creation_date = creation_date
        self.attachment = attachment
        self.channel_id = channel_id

class Snipe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.snipe_data = {}  # Dictionary to store snipe data per channel

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot:
            return

        channel = message.channel
        snipe_data = SnipeData(
            content=str(message.content),
            author=message.author,
            message_id=message.id,
            creation_date=str(message.created_at),
            attachment=message.attachments[0] if message.attachments else None,
            channel_id=channel.id
        )
        self.snipe_data[channel.id] = snipe_data

        await asyncio.sleep(60)

        if channel.id in self.snipe_data and message.id == self.snipe_data[channel.id].message_id:
            del self.snipe_data[channel.id]

    @app_commands.command(name='snipe', description='Get last deleted message')
    @app_commands.guild_only()
    async def snipe(self, inter):
        channel = inter.channel
        if channel.id not in self.snipe_data:
            await inter.response.send_message('There is nothing to snipe!', ephemeral=True)
            return

        snipe_data = self.snipe_data[channel.id]
        embed = discord.Embed(title=None, description=snipe_data.content)
        embed.set_author(name=f"{snipe_data.author} · at {snipe_data.creation_date[11:-16]}",
                         icon_url=snipe_data.author.display_avatar.url)

        if snipe_data.attachment is not None:
            embed.set_image(url=snipe_data.attachment.url)

        await inter.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Snipe(bot))
