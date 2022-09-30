from discord.ext import commands


class chain(commands.Cog):
    def __init__(self, ce):
        self.ce = ce

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.lower() != 'no' and message.channel.id == 1023251364006076506 and message.author.bot is False:
            await message.delete()


async def setup(ce):
    await ce.add_cog(chain(ce))