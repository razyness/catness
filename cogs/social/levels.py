from typing import Optional, List
import aiosqlite
import random
import discord
import typing
import asyncio
import aiohttp
import io
import easy_pil

from PIL import Image
from discord import app_commands, ui
from discord.interactions import Interaction
from data import Data, DATABASE_FILE
from discord.ext import commands
from collections import deque

async def load_server(table: str, server_id: str, columns: list = None) -> Optional[dict]:
	"""Get a dict of the contents of selected columns in a database's row
	Args:
		table (str): The name of the db table
		server_id (str): The column to search from
		columns (list): A list of column names to fetch
	Returns:
		Optional[dict]: A dictionary of the contents of the selected columns of that row
	"""
	async with aiosqlite.connect(DATABASE_FILE) as conn:
		if columns is None or columns == []:
			query_columns = "*"
		else:
			query_columns = f"{', '.join(columns)}"
		async with conn.execute(f"SELECT {query_columns} FROM {table} WHERE server_id = ?", (server_id,)) as cursor:
			row = await cursor.fetchone()
			if row is None:
				await conn.execute(f"INSERT INTO {table} (server_id) VALUES (?)", (server_id,))
				await conn.commit()
				async with conn.execute(f"SELECT {query_columns} FROM {table} WHERE server_id = ?", (server_id,)) as cursor:
					row = await cursor.fetchone()
		if columns is None or columns == []:
			columns = [description[0]
					   for description in cursor.description]
		data = dict(zip(columns, row))
	return data

async def fetch_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise ValueError(
                    f"Failed to fetch image, status code: {resp.status}")
            image_data = await resp.read()
            image = Image.open(io.BytesIO(image_data))
            return image


async def create_card(user_data):
    # Load the background image asynchronously
    background = await fetch_image(user_data['banner'])

    empty_canvas = easy_pil.Canvas(size=(1000, 620), color=(0, 0, 0, 0))

    editor = easy_pil.Editor(image=background)
    editor.resize(size=(int(1000/2), int(620/2)-40), crop=True)

    gradient_editor = easy_pil.Editor(image=empty_canvas)
    gradient = gradient_editor.rectangle(position=(
        0, 200/2), width=1000/2, height=500/2, color=(0, 0, 0, 130), radius=0)
    gradient = gradient.blur(mode="gussian", amount=200/2)
    editor.paste(gradient, (0, 0-10))

    profile_shadow_editor = easy_pil.Editor(image=empty_canvas)
    profile_shadow = profile_shadow_editor.rectangle(position=(
        98/2, 98/2), width=287/2, height=287/2, color=(0, 0, 0, 170), radius=40/2)
    profile_shadow = profile_shadow.blur(mode="gussian", amount=20/2)
    editor.paste(profile_shadow, (0, 0-10))

    avatar_image = await fetch_image(user_data['avatar'])
    avatar = easy_pil.Editor(avatar_image).resize(
        (int(287/2), int(287/2))).rounded_corners(radius=40/2)
    editor.paste(avatar, (int(98/2), int(98/2)-10))

    text_editor = easy_pil.Editor(image=empty_canvas)
    font_large = easy_pil.Font.montserrat(size=int(45/2), variant="bold")
    font_medium = easy_pil.Font.montserrat(size=int(32/2), variant="bold")
    font_small = easy_pil.Font.poppins(size=int(30/2), variant="bold")

    bar_editor = easy_pil.Editor(image=empty_canvas)
    bar_shadow = bar_editor.bar(position=(98/2, 404/2), max_width=787/2,
                                height=57/2, percentage=100, color=(0, 0, 0, 40), radius=15/2)
    bar_shadow.blur(mode="gussian", amount=20/2)
    editor.paste(bar_shadow, (0, 0-10))
    bar = bar_editor.bar(position=(98/2, 404/2), max_width=787/2, height=57/2,
                         percentage=100, color=(255, 255, 255, 70), radius=15/2)
    editor.paste(bar, (0, 0-10))
    bar_progress = bar_editor.bar(position=(98/2, 404/2), max_width=787/2, height=57/2,
                                  percentage=user_data['percentage'], color=(255, 255, 255, 230), radius=15/2)
    editor.paste(bar_progress, (0, 0-10))

    rep_bg_editor = easy_pil.Editor(image=empty_canvas)
    rep_shadow = rep_bg_editor.bar(position=(
        682/2, 333/2), max_width=205/2, height=57/2, percentage=100, color=(0, 0, 0, 40), radius=15/2)
    editor.paste(rep_shadow, (0, 0-10))
    rep_bg = rep_bg_editor.bar(position=(682/2, 333/2), max_width=205/2,
                               height=57/2, percentage=100, color=(255, 255, 255, 180), radius=15/2)
    editor.paste(rep_bg, (0, 0-10))

    username = text_editor.text(position=(
        433/2, 133/2), text=user_data["name"], color=(0, 0, 0, 40), font=font_large)
    exp_text = text_editor.text(position=(
        104/2, 468/2), text=f'{user_data["xp"]}/{user_data["next_level_xp"]}', color=(0, 0, 0, 30), font=font_small)
    level_text = text_editor.text(position=(
        880/2, 468/2), text=f'{user_data["level"]} > {user_data["level"] + 1}', color=(0, 0, 0, 30), align="right", font=font_small)
    text_editor.blur(mode="gussian", amount=5/2)

    for i in [username, exp_text, level_text]:
        editor.paste(i, (0, 0-10))

    username = text_editor.text(position=(
        433/2, 133/2), text=user_data["name"], color=(255, 255, 255, 200), font=font_large)
    exp_text = text_editor.text(position=(
        104/2, 468/2), text=f'{user_data["xp"]}/{user_data["next_level_xp"]}', color=(255, 255, 255, 80), font=font_small)
    level_text = text_editor.text(position=(
        880/2, 468/2), text=f'{user_data["level"]} > {user_data["level"] + 1}', color=(255, 255, 255, 80), align="right", font=font_small)
    rep_text = text_editor.text(position=(
        782/2, 350/2), text=f"+ {user_data['rep']} rep", color=(30, 30, 30), align="center", font=font_medium)

    for i in [username, exp_text, level_text, rep_text]:
        editor.paste(i, (0, 0-10))

    return editor.image_bytes


class Paginateness(ui.View):
    def __init__(self, embeds: List[discord.Embed]) -> None:
        super().__init__(timeout=180)

        self._embeds = embeds
        self._queue = deque(embeds)
        self._initial = embeds[0]
        self._length = len(embeds)
        self._current_page = 1
        for i in self._queue:
            i.set_footer(text=f"Page {self._current_page} of {self._length}")
        self.children[0].disabled = True

        if self._length == 1:
            self.children[1].disabled = True

    async def disable_all(self, msg="Timed out...", view=None):
        for i in self.children:
            i.disabled = True
        await self.msg.edit(content=msg, embed=None, view=view)

    async def on_timeout(self):
        await self.disable_all()

    async def update_buttons(self, inter):
        for i in self._queue:
            i.set_footer(text=f"Page {self._current_page} of {self._length}")

        if self._current_page == self._length:
            self.children[1].disabled = True
        else:
            self.children[1].disabled = False

        if self._current_page == 1:
            self.children[0].disabled = True
        else:
            self.children[0].disabled = False

        await inter.response.edit_message(view=self)

    @ui.button(label="<", style=discord.ButtonStyle.blurple)
    async def prev(self, inter, button):
        self._queue.rotate(-1)
        self._current_page -= 1
        embed = self._queue[0]

        await self.update_buttons(inter)
        await self.msg.edit(embed=embed)

    @ui.button(label=">", style=discord.ButtonStyle.blurple)
    async def next(self, inter, button):
        self._queue.rotate(1)
        self._current_page += 1
        embed = self._queue[0]

        await self.update_buttons(inter)
        await self.msg.edit(embed=embed)

    @ui.button(label='Exit', style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: ui.Button):

        await self.disable_all(msg="Bye-bye")
        self.value = False
        self.stop()
        await interaction.response.defer()
        await asyncio.sleep(2)
        await self.msg.delete()

    @property
    def initial(self) -> discord.Embed:
        return self._initial


class Levels(commands.Cog):
    def __init__(self, ce):
        self.ce = ce
        self.load_db = Data.load_db
        self._cd = commands.CooldownMapping.from_cooldown(
            1, 20.0, commands.BucketType.member)

    def experience_curve(self, level) -> int:
        return round(5 * (level ** 2) + (50 * level) + 100)

    async def update_user(self, user_id, exp):
        async with aiosqlite.connect(DATABASE_FILE) as db:
            row = await self.load_db(table='profiles', user_id=user_id, columns=["level", "exp"])
            level, current_exp = row["level"], row["exp"]
            new_exp = current_exp + exp

            while new_exp >= self.experience_curve(level):
                new_exp -= self.experience_curve(level)
                level += 1

            await db.execute("UPDATE profiles SET exp=?, level=? WHERE user_id=?", (new_exp, level, user_id,))
            await db.commit()

    async def get_level(self, user_id):
        row = await self.load_db(table='profiles', user_id=user_id, columns=["level"])
        return row["level"]

    async def get_exp(self, user_id):
        row = await self.load_db(table='profiles', user_id=user_id, columns=["exp"])
        return row["exp"]

    def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()

    @commands.Cog.listener("on_message")
    async def give_xp(self, message):
        has_levels_on = await Data.load_db(table="settings", user_id=message.author.id, columns=['levels'])
        if has_levels_on['levels'] == 0:
            return

        server_levels_on = await load_server(table="servers", server_id=message.guild.id)
        if server_levels_on['levels'] == 0:
            return

        ratelimit = self.get_ratelimit(message)
        if message.author.bot or ratelimit is not None:
            return
        user_id = message.author.id
        prev_level = await self.get_level(user_id)
        prev_exp = await self.get_exp(user_id)
        xp_given = random.randint(5, 15)
        await self.update_user(user_id, xp_given)
        new_exp = prev_exp + xp_given
        exp_needed = self.experience_curve(prev_level)
        if new_exp >= exp_needed:
            new_level = prev_level + 1
            async with aiosqlite.connect(DATABASE_FILE) as db:
                await db.execute("UPDATE profiles SET level=? WHERE user_id=?", (new_level, user_id,))
                await db.commit()
            if new_level > prev_level:
                await message.channel.send(f"{message.author.mention} is now level `{new_level}`! Your new goal is `{self.experience_curve(new_level)}`")

    def generate_progress_bar(self, max_value, progress_value, level):
        percent_progress = progress_value / max_value
        filled_chars = round(percent_progress * 30)
        progress_bar = "▮" * filled_chars + "▯" * (30 - filled_chars)
        max_value_str = f"{max_value}"
        xp_level_str = f" xp: {progress_value}/{max_value}{' '*(13-len(max_value_str)-len(str(progress_value)))}level: {level} -> {level + 1}"
        output_str = f"{xp_level_str}\n{' '}{progress_bar}"
        return output_str

    @app_commands.command(description="Display your total XP and the amount of XP needed to reach the next level.")
    @app_commands.describe(user="i think you can figure it out")
    async def rank(self, inter, user: discord.User = None):
        user = user or inter.user

        user_levels_on = await Data.load_db(table="settings", user_id=user.id, columns=['levels'])
        if user_levels_on['levels'] == 0:
            return await inter.response.send_message("Their level is turned off!!!!", ephemeral=True)

        user = await self.ce.fetch_user(user.id)
        if user.bot:
            await inter.response.send_message("Bots are not allowed a rank because i'm mean!!!", ephemeral=True)
            return

        server_levels_on = await load_server(table="servers", server_id=inter.guild.id)
        if server_levels_on['levels'] == 0:
            return await inter.response.send_message("Levels are disabled in this server", ephemeral=True)

        await inter.response.defer(thinking=True)

        levels_info = await Data.load_db(table="profiles", user_id=user.id, columns=["level", "exp"])
        level, exp = levels_info["level"], levels_info["exp"]
        missing = round(5 * (level ** 2) + (50 * level) + 100)
        settings = await Data.load_db(table="settings", user_id=user.id)
        if settings['experiments'] == 1:
            rep = await Data.load_db(table="rep", user_id=user.id)

            user_data = {  # Most likely coming from database or calculation
                # The user's name
                "name": str(user) if settings['private'] == 0 else user.name,
                "xp": exp,
                "next_level_xp": missing,
                "level": level,
                "percentage": (exp / missing) * 100,
                "rep": rep['rep'],
                "avatar": user.display_avatar.url,
                "banner": f"{user.banner.url[:-9]}?size=1024" if user.banner else "https://cdn.discordapp.com/attachments/912099940325523586/1104016078880919592/card.png"
            }

            card = await create_card(user_data=user_data)

            file = discord.File(fp=card, filename='card.png')
            await inter.followup.send(file=file)
        else:
            embed = discord.Embed(title=str(user))
            embed.set_thumbnail(url=user.display_avatar.url)
            bar = self.generate_progress_bar(
                max_value=missing, progress_value=exp, level=level)

            embed.description = f"```{bar}```"
            await inter.followup.send(embed=embed)

    @app_commands.command(name="top", description="Leaderboard of sorts and stuffs")
    @app_commands.describe(compact="Show less users per page, to fit on mobile")
    async def top(self, inter: discord.Interaction, compact: bool = False):
        await inter.response.defer(thinking=True)
        compact = 6 if compact else 12
        conn = await aiosqlite.connect(DATABASE_FILE)
        cursor = await conn.cursor()

        await cursor.execute("SELECT user_id, level, exp FROM profiles")
        rows = await cursor.fetchall()

        profile_list = []

        for row in rows:
            user_id, level, exp = row

            settings = await Data.load_db(table="settings", user_id=user_id)
            user = str(self.ce.get_user(user_id) or await self.ce.fetch_user(user_id))
            if settings['private'] == 1:
                user = f"{user[:-4]}????"

            profile_dict = {
                'user': user,
                'level': level,
                'exp': exp
            }

            if settings['levels'] != 0:
                profile_list.append(profile_dict)

            if len(profile_list) >= 30:
                break

        await conn.close()

        profile_list.sort(key=lambda user: (
            user['level'], user['exp']), reverse=True)

        embeds = []
        pos = 1
        for i in range(0, len(profile_list), compact):
            embed = discord.Embed(title="Leaderboard of the levels real")

            for profile in profile_list[i:i+compact]:
                user = profile['user']
                level = profile['level']
                exp = profile['exp']
                flair = f"{pos}"
                if pos == 1:
                    flair = f"🥇"
                elif pos == 2:
                    flair = f"🥈"
                elif pos == 3:
                    flair = f"🥉"
                embed.add_field(name=f"{flair}. {user}",
                                value=f"Level `{level}`/`{exp}`xp")
                pos += 1

            embeds.append(embed)

        view = Paginateness(embeds)
        await inter.followup.send(embed=view.initial, view=view)
        view.msg = await inter.original_response()


async def setup(ce):
    await ce.add_cog(Levels(ce))
