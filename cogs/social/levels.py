import aiosqlite
import random
import discord
import typing
import asyncio
import aiohttp
import io
import easy_pil

from typing import Optional, List

from PIL import Image

from discord import app_commands, ui
from discord.ext import commands

from data import Data, DATABASE_FILE, icons
from utils import cache


@cache.cache(360, 60)
async def get_lb_page(bot, page_number: int, compact: bool) -> tuple:
    compact_size = 6 if compact else 12
    offset = (page_number - 1) * compact_size

    query = """
    SELECT id, level, exp
    FROM (
        SELECT profiles.id, profiles.level, profiles.exp,
        ROW_NUMBER() OVER (ORDER BY profiles.level DESC, profiles.exp DESC, profiles.id ASC) AS row_num
        FROM profiles
        JOIN settings ON profiles.id = settings.id
        WHERE settings.levels != 0 AND profiles.exp != 0
    )
    WHERE row_num BETWEEN ? AND ?
    """
    count_query = """
    SELECT COUNT(*) AS total_rows
    FROM profiles
    JOIN settings ON profiles.id = settings.id
    WHERE settings.levels != 0 AND profiles.exp != 0
    """

    async with aiosqlite.connect(DATABASE_FILE) as conn:
        cursor = await conn.execute(query, (offset + 1, offset + compact_size))
        rows = await cursor.fetchall()

        count_cursor = await conn.execute(count_query)
        total_rows = (await count_cursor.fetchone())[0]
        total_pages = (total_rows // compact_size) + 1

        if page_number < 1 or page_number > total_pages:
            return None, total_pages

        embed = discord.Embed(title="Leaderboard of the levels real")
        pos = offset + 1

        for row in rows:
            user_id, level, exp = row
            user = str(bot.get_user(user_id) or await bot.fetch_user(user_id))
            flair = "🥇" if pos == 1 else "🥈" if pos == 2 else "🥉" if pos == 3 else str(
                pos)
            embed.add_field(name=f"{flair}. {user}",
                            value=f"Level `{level}`/`{exp}`xp")
            pos += 1

        embed.set_footer(text=f"Page {page_number} of {total_pages}")

    return embed, total_pages


async def fetch_image(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise ValueError(
                    f"Failed to fetch image, status code: {resp.status}")
            image_data = await resp.read()
            image = Image.open(io.BytesIO(image_data))
            return image

@cache.cache(360, 60)
async def create_card(user_data):
    background = await fetch_image(user_data['banner'])
    empty_canvas = easy_pil.Canvas(size=(1000, 620), color=(0, 0, 0, 0))
    editor = easy_pil.Editor(image=background)
    editor.resize(size=(int(1000/2), int(620/2)-40), crop=True)

    # Create a separate canvas for blurred elements
    blur_editor = easy_pil.Editor(image=empty_canvas)

    profile_shadow_editor = easy_pil.Editor(image=empty_canvas)
    profile_shadow = profile_shadow_editor.rectangle(position=(
        98/2, 98/2), width=287/2, height=287/2, color=(0, 0, 0, 90), radius=40/2)
    blur_editor.paste(profile_shadow, (0, 0-10))

    gradient_editor = easy_pil.Editor(image=empty_canvas)
    gradient = gradient_editor.rectangle(position=(
        0, 0), width=1000/2, height=600/2, color=(0, 0, 0, 30), radius=0)
    editor.paste(gradient, (0, 0-10))

    rep_blur_editor = easy_pil.Editor(image=empty_canvas)
    rep_shadow = rep_blur_editor.bar(position=(
        682/2, 333/2), max_width=205/2, height=57/2, percentage=100, color=(0, 0, 0, 90), radius=15/2)
    blur_editor.paste(rep_shadow, (0, 0-10))

    text_editor = easy_pil.Editor(image=empty_canvas)
    font_large = easy_pil.Font.montserrat(size=int(45/2), variant="bold")
    font_medium = easy_pil.Font.montserrat(size=int(32/2), variant="bold")
    font_small = easy_pil.Font.poppins(size=int(30/2), variant="bold")

    username = text_editor.text(position=(
        433/2, 133/2), text=user_data["name"], color=(0, 0, 0, 90), font=font_large)
    exp_text = text_editor.text(position=(
        104/2, 468/2), text=f'{user_data["xp"]}/{user_data["next_level_xp"]}', color=(0, 0, 0, 90), font=font_small)
    level_text = text_editor.text(position=(
        880/2, 468/2), text=f'{user_data["level"]} > {user_data["level"] + 1}', color=(0, 0, 0, 90), align="right", font=font_small)
    
    blur_editor.paste(username, (0, 0-10))
    blur_editor.paste(exp_text, (0, 0-10))
    blur_editor.paste(level_text, (0, 0-10))

    bar_editor = easy_pil.Editor(image=empty_canvas)
    bar_shadow = bar_editor.bar(position=(98/2, 404/2), max_width=787/2,
                                height=57/2, percentage=100, color=(0, 0, 0, 90), radius=15/2)
    
    blur_editor.paste(bar_shadow, (0, 0-10))

    # Continue adding other elements to the blurred canvas

    # Apply blur effect to the blurred canvas
    
    blur_editor.blur(mode="gussian", amount=20/2)

    # Paste the blurred canvas onto the main canvas
    editor.paste(blur_editor, (0, 5))
    
    bar = bar_editor.bar(position=(98/2, 404/2), max_width=787/2, height=57/2,
                         percentage=100, color=(255, 255, 255, 70), radius=15/2)
    editor.paste(bar, (0, 0-10))
    bar_progress = bar_editor.bar(position=(98/2, 404/2), max_width=787/2, height=57/2,
                                  percentage=user_data['percentage'], color=(255, 255, 255, 230), radius=15/2)
    editor.paste(bar_progress, (0, 0-10))

    rep_bg_editor = easy_pil.Editor(image=empty_canvas)
    rep_bg = rep_bg_editor.bar(position=(682/2, 333/2), max_width=205/2,
                               height=57/2, percentage=100, color=(255, 255, 255, 180), radius=15/2)
    editor.paste(rep_bg, (0, 0-10))

    avatar_image = await fetch_image(user_data['avatar'])
    avatar = easy_pil.Editor(avatar_image).resize(
        (int(287/2), int(287/2))).rounded_corners(radius=40/2)
    editor.paste(avatar, (int(98/2), int(98/2)-10))

    username = text_editor.text(position=(
        433/2, 133/2), text=user_data["name"], color=(255, 255, 255, 200), font=font_large)
    exp_text = text_editor.text(position=(
         104/2, 468/2), text=f'{user_data["xp"]}/{user_data["next_level_xp"]}', color=(255, 255, 255, 140), font=font_small)
    level_text = text_editor.text(position=(
         880/2, 468/2), text=f'{user_data["level"]} > {user_data["level"] + 1}', color=(255, 255, 255, 140), align="right", font=font_small)
    rep_text = text_editor.text(position=(
         782/2, 350/2), text=f"+ {user_data['rep']} rep", color=(30, 30, 30), align="center", font=font_medium)

    editor.paste(username, (0, 0-10))
    editor.paste(exp_text, (0, 0-10))
    editor.paste(level_text, (0, 0-10))
    editor.paste(rep_text, (0, 0-10))

    return editor.image_bytes


class Paginateness(ui.View):
    def __init__(self, bot, pages: int, compact: bool) -> None:
        super().__init__(timeout=180)

        self._compact = compact
        self._pages = pages
        self._current_page = 1
        self._bot = bot
        self.children[0].disabled = True

        if self._pages == 1:
            self.children[1].disabled = True

    async def disable_all(self, msg="Timed out...", view=None):
        for i in self.children:
            i.disabled = True
        await self.msg.edit(content=msg, embed=None, view=view)

    async def on_timeout(self):
        await self.disable_all()

    async def update_buttons(self, inter):
        if self._current_page == self._pages:
            self.children[1].disabled = True
        else:
            self.children[1].disabled = False

        if self._current_page == 1:
            self.children[0].disabled = True
        else:
            self.children[0].disabled = False

        await inter.response.edit_message(view=self)

    @ui.button(emoji=icons.page_left, style=discord.ButtonStyle.blurple)
    async def prev(self, inter, button):

        self._current_page -= 1
        embed = await get_lb_page(bot=self._bot, page_number=self._current_page, compact=self._compact)
        await self.update_buttons(inter)
        await self.msg.edit(embed=embed[0])
        self._pages = embed[1]

    @ui.button(emoji=icons.page_right, style=discord.ButtonStyle.blurple)
    async def next(self, inter, button):
        self._current_page += 1
        embed = await get_lb_page(bot=self._bot, page_number=self._current_page, compact=self._compact)
        await self.update_buttons(inter)
        await self.msg.edit(embed=embed[0])
        self._pages = embed[1]

    @ui.button(emoji=icons.close, style=discord.ButtonStyle.red)
    async def close(self, interaction: discord.Interaction, button: ui.Button):

        await self.disable_all(msg="Bye-bye")
        self.value = False
        self.stop()
        await interaction.response.defer()
        await asyncio.sleep(2)
        await self.msg.delete()


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
            row = await self.load_db(table='profiles', id=user_id, columns=["level", "exp"])
            level, current_exp = row["level"], row["exp"]
            new_exp = current_exp + exp

            while new_exp >= self.experience_curve(level):
                new_exp -= self.experience_curve(level)
                level += 1

            await db.execute("UPDATE profiles SET exp=?, level=? WHERE id=?", (new_exp, level, user_id,))
            await db.commit()

    async def get_level(self, user_id):
        row = await self.load_db(table='profiles', id=user_id, columns=["level"])
        return row["level"]

    async def get_exp(self, user_id):
        row = await self.load_db(table='profiles', id=user_id, columns=["exp"])
        return row["exp"]

    def get_ratelimit(self, message: discord.Message) -> typing.Optional[int]:
        bucket = self._cd.get_bucket(message)
        return bucket.update_rate_limit()

    @commands.Cog.listener("on_message")
    async def give_xp(self, message):
        has_levels_on = await Data.load_db(table="settings", id=message.author.id, columns=['levels'])
        if has_levels_on['levels'] == 0:
            return

        if message.guild:
            server_levels_on = await Data.load_db(table="servers", id=message.guild.id)
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
                await db.execute("UPDATE profiles SET level=? WHERE id=?", (new_level, user_id,))
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
    @cache.cache(360, 60)
    async def rank(self, inter, user: discord.User = None):
        user = user or inter.user

        user_levels_on = await Data.load_db(table="settings", id=user.id, columns=['levels'])
        if user_levels_on['levels'] == 0:
            return await inter.response.send_message("Their level is turned off!!!!", ephemeral=True)

        user = await self.ce.fetch_user(user.id)
        if user.bot:
            await inter.response.send_message("Bots are not allowed a rank because i'm mean!!!", ephemeral=True)
            return

        if inter.guild:
            server_levels_on = await Data.load_db(table="servers", id=inter.guild.id)
            if server_levels_on['levels'] == 0:
                return await inter.response.send_message("Levels are disabled in this server", ephemeral=True)

        await inter.response.defer(thinking=True)

        levels_info = await Data.load_db(table="profiles", id=user.id, columns=["level", "exp"])
        level, exp = levels_info["level"], levels_info["exp"]
        missing = round(5 * (level ** 2) + (50 * level) + 100)
        settings = await Data.load_db(table="settings", id=user.id)
        if settings['experiments'] == 1:
            rep = await Data.load_db(table="rep", id=user.id)

            user_data = {
                "name": user.name if settings['private'] == 0 else user.global_name,
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
    @cache.cache(360, 60)
    async def top(self, inter: discord.Interaction, compact: bool = False):
        await inter.response.defer(thinking=True)
        embed, pages = await get_lb_page(self.ce, 1, compact)
        embed.set_footer(text=f"Page 1 of {pages}")
        view = Paginateness(self.ce, pages, compact)
        await inter.followup.send(embed=embed, view=view)
        view.msg = await inter.original_response()


async def setup(ce):
    await ce.add_cog(Levels(ce))
