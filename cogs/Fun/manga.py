from __future__ import annotations
from typing import List, Optional

import discord
import aiohttp
import asyncio

from discord.ext import commands
from discord import app_commands

from datetime import datetime

from utils import icons


def sort_chapters(chapters):
    """Sorts chapters in order, synchronously

    Args:
            chapters (list): a json or dict of the api response. See async get_chapters

    Returns:
            tuple: a list of tuples containing (chapter_number, chaptern_name, chapter_id)
    """
    sorted_chapters = sorted(
        chapters, key=lambda x: float(x['attributes']['chapter']))

    chapter_list = [(chapter['attributes']['chapter'],
                     chapter['attributes']['title'], chapter['id']) for chapter in sorted_chapters]

    return chapter_list


async def get_chapters(manga_id, session, languages=['en']):
    """Returns a list of chapter ids for a given manga and language

    Args:
            manga_id (str): Manga id on MangaDex
            session (aiohttp.ClientSession): The aiohttp session

            languages (list, optional): A list of languages in the ISO format. Defaults to ['en'].

    Returns:
            list: a list of touples containing (chapter_number, chaptern_name, chapter_id)
    """
    base_url = "https://api.mangadex.org"
    r = await session.get(
        f"{base_url}/manga/{manga_id}/feed",
        params={"translatedLanguage[]": languages})

    return sort_chapters(r['data'])


async def get_page_url(manga_id, chapter, page, session):
    """Get a single page url given a manga, chaper and page

    Args:
            manga_id (str): Manga id on MangaDex
            chapter (tuple): The chapter object, (chapter_number, chaptern_name, chapter_id)
            page (int): The page number, starting from 0
            session (aiohttp.ClientSession): The aiohttp session

    Returns:
            str: a direct url of the page
    """
    base_url = "https://api.mangadex.org/at-home/server"

    c = await get_chapters(manga_id)
    c = await session.get(f"{base_url}/{c[chapter][2]}")
    chapter_hash = c['chapter']['hash']
    data = c["chapter"]["data"][page]
    return f"https://uploads.mangadex.org/data/{chapter_hash}/{data}"


async def get_pages_count(chapter, session):
    """Simply returns the amount of pages in a chapter

    Args:
            chapter (tuple): The chapter object, (chapter_number, chaptern_name, chapter_id)
            session (aiohttp.ClientSession): The aiohttp session

    Returns:
            int: Amount of pages
    """
    base_url = "https://api.mangadex.org/at-home/server"

    r = await session.get(f"{base_url}/{chapter}")
    return len(r["chapter"]["data"])


class JumpModal(discord.ui.Modal, title="Jump to"):
    def __init__(self, msg, max, view):
        self.max = max
        self.msg = msg
        self.og_view = view

        self.page = discord.ui.TextInput(
            label='index', style=discord.TextStyle.short, placeholder=f"1/{self.max}")

    async def on_submit(self, inter):
        if not self.page.value.isdigit():
            return await inter.response.send_message("Invalid input")

        if int(self.page.value) > self.max:
            self.page.value = self.max

        await inter.response.send_message(f"Jumping to page {self.page.value}")

        page_url = await get_page_url(self.manga_id, self._chapter, self.page.value)
        embed = self.msg.embed
        embed.set_image(url=page_url)
        embed.set_footer(
            text=f"Ch.{self._chapter + 1}/{len(self._chapter_list)}  •  Pg.{self.page.value}/{self._pages}")
        await self.msg.edit(embed=embed, view=self.og_view)


class ViewThing(discord.ui.View):
    def __init__(self, *, timeout: float | None = 180, manga_id, manga_title, session):
        super().__init__(timeout=timeout)
        self.manga_id = manga_id
        self.manga_title = manga_title
        self.sesison = session

    @discord.ui.button(style=discord.ButtonStyle.blurple, label="Start Reading")
    async def read(self, inter: discord.Interaction, button):

        chapters = await get_chapters(self.manga_id)
        pages = await get_pages_count(chapters[0][2])
        first_page = await get_page_url(self.manga_id, 0, 0)

        embed = discord.Embed(title=f"Chapter 1: {chapters[0][1]}")
        embed.set_footer(text=f"Ch.1/{len(chapters)}  •  Pg.1/{pages}")
        embed.set_image(url=first_page)
        embed.set_author(name=self.manga_title,
                         url=f"https://mangadex.org/title/{self.manga_id}")

        view = Reader(manga_id=self.manga_id,
                      manga_title=self.manga_title, chapters=chapters, pages=pages)
        await inter.response.send_message(embed=embed, view=view, ephemeral=True)
        view.msg = await inter.original_response()


class Reader(discord.ui.View):
    def __init__(self, *, timeout: float | None = 540, manga_id, manga_title, chapters, pages):
        super().__init__(timeout=timeout)
        self.manga_id = manga_id
        self.manga_title = manga_title
        self._pages = pages
        self._chapter_list = chapters

        self._page = 0
        self._chapter = 0

        self.children[0].disabled = True

    @discord.ui.button(emoji=icons.page_left, style=discord.ButtonStyle.blurple)
    async def back(self, inter, button):

        self._page -= 1
        if self._page < 0:
            self._chapter -= 1
            self._pages = await get_pages_count(self._chapter_list[self._chapter][2])
            self._page = self._pages - 1

        page_url = await get_page_url(self.manga_id, self._chapter, self._page)
        embed = discord.Embed(
            title=f"Chapter {self._chapter + 1}: {self._chapter_list[self._chapter][1]}")
        embed.set_image(url=page_url)
        embed.set_footer(
            text=f"Ch.{self._chapter + 1}/{len(self._chapter_list)}  •  Pg.{self._page + 1}/{self._pages}")
        embed.set_author(name=self.manga_title,
                         url=f"https://mangadex.org/title/{self.manga_id}")
        await inter.response.defer()

        if 0 < self._page < self._pages:
            for i in self.children:
                i.disabled = False
        elif 0 >= self._page and 0 >= self._chapter:
            button.disabled = True
        elif self._page >= self._pages and self._chapter >= len(self._chapter_list):
            self.children[1].disabled = True

        await self.msg.edit(embed=embed, view=self)

    @discord.ui.button(emoji=icons.page_right, style=discord.ButtonStyle.blurple)
    async def forward(self, inter, button):

        self._page += 1
        if self._page >= self._pages:
            if self._chapter <= len(self._chapter_list):
                self._chapter += 1
                self._page = 0

        self._pages = await get_pages_count(self._chapter_list[self._chapter][2])

        page_url = await get_page_url(self.manga_id, self._chapter, self._page)
        embed = discord.Embed(
            title=f"Chapter {self._chapter + 1}: {self._chapter_list[self._chapter][1]}")
        embed.set_image(url=page_url)
        embed.set_author(name=self.manga_title,
                         url=f"https://mangadex.org/title/{self.manga_id}")
        embed.set_footer(
            text=f"Ch.{self._chapter + 1}/{len(self._chapter_list)}  •  Pg.{self._page + 1}/{self._pages}")
        await inter.response.defer()

        if 0 < self._page < self._pages:
            for i in self.children:
                i.disabled = False
        elif 0 >= self._page and 0 >= self._chapter:
            self.children[0].disabled = True
        elif self._page >= self._pages and self._chapter >= len(self._chapter_list):
            button.disabled = True

        await self.msg.edit(embed=embed, view=self)

    @discord.ui.button(label="Ch.", emoji=icons.edit)
    async def jump(self, inter, button):
        modal = JumpModal(self.msg, self._pages, self)
        await inter.response.send_modal(modal)


class Search(commands.Cog):
    """A not so fully featured manga search and reader command for mangadex.org"""
    def __init__(self, bot):
        self.bot = bot

    group = app_commands.Group(
        name="mangadex", description="Manga command yay")

    def format_number(self, number):
        if number < 1000:
            return str(number)
        elif number < 1000000:
            return '{:.1f}K'.format(number / 1000)
        else:
            return '{:.1f}M'.format(number / 1000000)

    def format_string(self, string, limit):
        if len(string) <= limit:
            return string

        words = string.split()
        truncated_words = []

        for word in words:
            if len(' '.join(truncated_words + [word])) > limit:
                break
            truncated_words.append(word)

        truncated_string = ' '.join(truncated_words)

        if truncated_string.endswith(','):
            truncated_string = truncated_string[:-1]

        truncated_string = truncated_string[:limit - 3] + '...'

        return truncated_string

    async def query_autocomplete(self, inter, current: str) -> List[app_commands.Choice[str]]:
        url = f"https://api.mangadex.org/manga?title={current}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise Exception("Failed to fetch manga search results")

                data = await response.json()
                results = data["data"]

                manga_list = []
                for result in results:
                    manga_title = result["attributes"]["title"]["en"]
                    manga_url = f"https://api.mangadex.org/manga/{result['id']}?includes[]=cover_art"
                    manga_list.append(app_commands.Choice(
                        name=manga_title, value=manga_url))

                return manga_list

    @group.command(name="search", description="Search manga from mangadex.org")
    @app_commands.describe(query="Search query")
    @app_commands.autocomplete(query=query_autocomplete)
    async def search(self, inter, query: str):
        async with self.bot.web_client.get(query) as r:
            r = await r.json()
            data = r["data"]
            
        desc = data["attributes"]["description"]['en'] if data["attributes"]["description"] != {
        } or not data["attributes"]["description"] else "*No description provided*"
        embed = discord.Embed(
            title=data["attributes"]["title"]["en"], description=self.format_string(desc, 4096))
        embed.set_author(name="open in MangaDex", url=f"https://mangadex.org/title/{data['id']}",
                         icon_url="https://pbs.twimg.com/profile_images/1391016345714757632/xbt_jW78_400x400.jpg")
        embed.add_field(name=f"Status: `{data['attributes']['status'].capitalize()}`", value=f"Created <t:{int(datetime.fromisoformat(data['attributes']['createdAt']).timestamp())}:R>\n"
                        f"Updated <t:{int(datetime.fromisoformat(data['attributes']['updatedAt']).timestamp())}:R>")

        tags = ", ".join(
            f"[`{tag['attributes']['name']['en']}`](https://mangadex.org/tag/{tag['id']})" for tag in data["attributes"]["tags"])

        embed.add_field(name="Genres", value=self.format_string(tags, 1024))

        for relationship in data["relationships"]:
            if relationship["type"] == "cover_art":
                cover_art_id = relationship["attributes"]["fileName"]
                break
        
        async with self.bot.web_client.get(f"https://api.mangadex.org/statistics/manga/{data['id']}") as r:
            r = await r.json()
            stats = r['statistics'][data['id']]

        embed.set_footer(
            text=f"📈 {round(stats['rating']['bayesian'], 2)}  • ⭐ {round(stats['rating']['average'], 2)}  • 🏷️ {self.format_number(stats['follows'])}")
        embed.set_thumbnail(
            url=f"https://uploads.mangadex.org/covers/{data['id']}/{cover_art_id}")

        view = ViewThing(
            manga_id=data['id'], manga_title=data["attributes"]["title"]["en"], session=self.bot.web_client)
        await inter.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Search(bot))
