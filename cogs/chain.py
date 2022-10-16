from discord.ext import commands


class chain(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower() != '😺' and message.channel.id == 1029553983259414588:
            await message.delete()

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.content.lower() != '😺' and after.channel.id == 1029553983259414588:
            await after.delete()


async def setup(client):
    await client.add_cog(chain(client))