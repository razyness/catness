import discord
from datetime import timedelta
from discord.ext import commands


class Antispam(commands.Cog):
    def __init__(self, ce):
        self.anti_spam = commands.CooldownMapping.from_cooldown(5, 10, commands.BucketType.member)
        self.too_many_violations = commands.CooldownMapping.from_cooldown(5, 60, commands.BucketType.member)
        self.ce = ce

    @commands.Cog.listener()
    async def on_message(self, message):
        if type(message.channel) is not discord.TextChannel or message.author.bot:
            return

        bucket = self.anti_spam.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            await message.delete()
            await message.channel.send(f'{message.author.mention} you\'re sending messages too fast!', delete_after=5)
            violations = self.too_many_violations.get_bucket(message)
            check = violations.update_rate_limit()
            if check:
                await message.author.timeout(timedelta(minutes=10), reason='Spamming')
                embed = discord.Embed(title=f'You were muted in **{message.guild.name}** for spamming!')
                await message.author.send(embed=embed)


async def setup(ce):
    await ce.add_cog(Antispam(ce))
