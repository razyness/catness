import discord
from discord.ext import commands

class Penis(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def penis_detector(text):
        words = text.split()
        highlighted_text = ""
        for i in range(len(words) - 4):
            if (words[i][0].lower() == 'p' and
                words[i+1][0].lower() == 'e' and
                words[i+2][0].lower() == 'n' and
                words[i+3][0].lower() == 'i' and
                words[i+4][0].lower() == 's'):
                for j in range(i, i+5):
                    highlighted_text += f"**{words[j][0]}**{words[j][1:]} "
                return highlighted_text.strip()
        return False

    @commands.Cog.listener(event="on_message")
    async def penis(self, message):
        if result:=penis_detector(message.content):
            embed = discord.Embed(title="Hidden penis detected!")
            embed.description = f"Penis found: {result}"
            await message.reply(embed=embed)

async def setup(bot):
    await bot.add_cog(Penis(bot))
