import discord
import random
import json

from discord import app_commands
from discord.ext import commands, tasks
from discord.app_commands import Choice

from datetime import datetime
from utils import blocking

class Cake(commands.Cog):
	MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
			  'August', 'September', 'October', 'November', 'December']
	
	def __init__(self, bot):
		super().__init__()
		self.bot = bot

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
	async def cake(self, inter, day: int, month: str, year: int, consider: bool = True):
		cake_date = f"{day}/{month}/{year}"
		cake_strptime = self.parse_date(date_str=cake_date)
		if not cake_strptime:
			await inter.response.send_message(f"`{cake_date}` is not a valid date!!")
			return
		
		cake_format = {
			"day": day,
			"month": int(month),
			"year": year,
			"consider": consider
		}

		user_id = inter.user.id

		cake_format = await blocking.run(lambda: json.dumps(cake_format))

		async with self.bot.db_pool.acquire() as conn:
			async with conn.transaction():
				await conn.execute("INSERT INTO profiles (id) VALUES ($1) ON CONFLICT DO NOTHING", user_id)
				await conn.execute("UPDATE profiles SET cake=$1 WHERE id=$2", cake_format, user_id)
	
		response = f"Your cake day is set to <t:{int(cake_strptime.timestamp())}:D>! The year is `{str(consider).replace('True', 'Public').replace('False', 'Private')}`"
		await inter.response.send_message(response, ephemeral=True)


	@tasks.loop(hours=24)
	async def cakeloop(self):
		date = datetime.today().strftime('%d/%m/%Y')
		day, month, year = date.split("/")
		async with self.bot.db_pool.acquire() as conn:
			async with conn.transaction():
				rows = await conn.fetchall("SELECT id, cake, follows FROM profiles")
				rows = [dict(row) for row in rows]
	
			for row in rows:
				user_id = row[0]
				cake_date = row[1]
				follows = row[2]

				if cake_date is None or cake_date == {}:
					continue
				
				if cake_date["day"] == day and cake_date["month"] == month:
					cake_user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
					if follows == {}:
						continue
					following = follows.get("following", [])
					followers = follows.get("followers", [])
					for i in following + followers:
						notif_user = await self.bot.fetch_user(i)
						embed = discord.Embed(title=str(cake_user))
						embed.set_thumbnail(url=cake_user.display_avatar.url)
						c = [
							"🎉 Happy Birthday, {user}! Let's party!",
							"🎂 It's {user}'s birthday, Wish them a wonderful day!",
							"🎉 It's {user}'s special day! Celebrate!",
							"🎁 Cheers to another year! Happy Birthday, {user}!",
							"🎉 Let's celebrate {user}'s birthday! Enjoy the day!"
						]
						embed.description = random.choice(
							c).replace("{user}", cake_user.mention)
						embed.set_footer(text="You can unsubscribe from their profile with `/profile`")
						if cake_date["consd"]:
							embed.description = f"{embed.description}\nThey are turning `{int(year) - int(cake_date['year'])}`"
							await notif_user.send(embed=embed)
						else:
							await notif_user.send(embed=embed)
	
async def setup(bot):
	await bot.add_cog(Cake(bot))
