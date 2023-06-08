import aiosqlite

from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice

from datetime import datetime

from data import Data, DATABASE_FILE


class Cake(commands.Cog):
    MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
              'August', 'September', 'October', 'November', 'December']
    
    def __init__(self, ce):
        super().__init__()
        self.ce = ce

    def parse_date(self, date_str):
        try:
            date = datetime.strptime(date_str, "%d/%m/%Y")
            if date.date() > datetime.now().date():
                return None
            return date
        except ValueError:
            return None

    @app_commands.command(
        name="cake",
        description="Set a birthdate to display on your profile, along with other benefits!!"
    )
    @app_commands.choices(month=[Choice(name=month, value=f'{(num+1):02}')
                                 for num, month in enumerate(MONTHS)])
    @app_commands.describe(consider="Consider the year to inform others of your age?")
    async def cake(self, inter, day: int, month: Choice[str], year: int, consider: bool = True):
        cake_date = f"{day}/{month.value}/{year}"
        cake_strptime = self.parse_date(date_str=cake_date)
        if not cake_strptime:
            await inter.response.send_message(f"`{cake_date}` is not a valid date!!")
            return
        cake_format = f"{cake_date}:{consider}"
        user_id = str(inter.user.id)
        data = await Data.load_db("profiles", user_id)
        if data is None:
            async with aiosqlite.connect(DATABASE_FILE) as conn:
                await conn.execute(f"INSERT INTO profiles (id) VALUES (?)", (user_id,))
                await conn.commit()
        async with aiosqlite.connect(DATABASE_FILE) as conn:
            await conn.execute(f"UPDATE profiles SET cake=? WHERE id=?", (cake_format, user_id))
            await conn.commit()

        response = f"Your cake day is set to <t:{int(cake_strptime.timestamp())}:D>! The year is `{str(consider).replace('True', 'Public').replace('False', 'Private')}`"

        await inter.response.send_message(response, ephemeral=True)


async def setup(ce):
    await ce.add_cog(Cake(ce))
