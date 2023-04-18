import aiosqlite
import json

from discord import app_commands
from discord.ext import commands, tasks
from discord.app_commands import Choice

from datetime import datetime

from data import Data, DATABASE_FILE


class Cake(commands.Cog):
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

	@app_commands.command(name="cake", description="Set a birthdate to display on your profile, along with other benefits!!")
	@app_commands.choices(month=[Choice(name='January', value="01"), Choice(name='February', value="02"), Choice(name='March', value="03"),
								 Choice(name='April', value="04"), Choice(
									 name='May', value="05"), Choice(name='June', value="06"),
								 Choice(name='July', value="07"), Choice(
									 name='August', value="08"), Choice(name='September', value="09"),
								 Choice(name='October', value="10"), Choice(name='November', value="11"), Choice(name='December', value="12")])
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
				await conn.execute(f"INSERT INTO profiles (user_id) VALUES (?)", (user_id,))
				await conn.commit()
		async with aiosqlite.connect(DATABASE_FILE) as conn:
			await conn.execute(f"UPDATE profiles SET cake=? WHERE user_id=?", (cake_format, user_id))
			await conn.commit()

		response = f"Your cake day is set to <t:{int(cake_strptime.timestamp())}:D>! The year is `{str(consider).replace('True', 'Public').replace('False', 'Private')}`"

		await inter.response.send_message(response, ephemeral=True)

	@tasks.loop(hours=12)
	async def cakeloop(self):
		date = datetime.datetime.today().strftime('%d/%m/%Y')
		day, month, year = date.split("/")
		async with aiosqlite.connect(DATABASE_FILE) as conn:
			async with conn.execute("SELECT user_id, cake, follow_list FROM profiles") as cursor:
				rows = await cursor.fetchall()
			follow_lists = {}
			for row in rows:
				user_id = row[0]
				cake_str = row[1]
				cake_parts = cake_str.split(":")
				cake_date = cake_parts[0]
				cake_bool = cake_parts[1].lower() == "true"
				cake_day, cake_month, cake_year = cake_date.split("/")
				if cake_day == day and cake_month == month:
					follow_list_str = row[2]
					if follow_list_str:
						follow_list = json.loads(follow_list_str)
						follow_lists[user_id] = {
							"follow_list": follow_list,
							"has_birthday": cake_bool
						}
				cake_user = await self.ce.fetch_user(user_id)
				for i in follow_list[follow_list]:
					user = self.ce.fetch_user(i)
					if cake_bool:
						await user.send(f"🎉 It's {cake_user.mention}'s birthday! They are turning `{int(year) - int(cake_year)}`")
					else:
						await user.send(f"🎉 It's {cake_user.mention}'s birthday!")





	@commands.Cog.listener()
	async def on_ready(self):
		if not self.cakeloop.is_running():
			await self.cakeloop.start()
			print("cake loop has begun")


async def setup(ce):
	await ce.add_cog(Cake(ce))
