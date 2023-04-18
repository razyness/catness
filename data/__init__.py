import sqlite3
import aiosqlite
import toml
import os

from typing import Optional

DATABASE_FILE = 'data/data.db'
config = toml.load("data/config.toml")


icons = {
    "edit": "<:edit:1062784953399648437>",
    "regen": "<:regen:1062784969749045318>",
    "download": "<:download:1062784992243105813>",
    "spotify_white": "<:spotify_white:1062784981203689472>",
    "bookmark": "<:bookmark:1062790109491114004>",
    "remove": "<:remove:1062791085404999781>",
    "active_developer": "<:Active_Developer:1078093417680224356>",
    "bot_http_interactions": "<:Supports_Commands:1078022481144729620>",
    "bug_hunter": "<:Bug_Hunter:1078015408684142743>",
    "bug_hunter_level_2": "<:Bug_Hunter_Level_2:1078015437285097542>",
    "discord_certified_moderator": "<:Discord_Mod_Alumni:1078091018886451281>",
    "early_supporter": "<:Early_Supporter:1078015810909524149>",
    "early_verified_bot_developer": "<:Verified_Bot_Developer:1078094815398461450>",
    "hypesquad": "<:HypeSquad_Event:1078014370912686180>",
    "hypesquad_balance": "<:HypeSquad_Balance:1078014406396485642>",
    "hypesquad_bravery": "<:HypeSquad_Bravery:1078014366953242794>",
    "hypesquad_brilliance": "<:HypeSquad_Brilliance:1078014368454820010>",
    "partner": "<:Discord_Partner:1078021591859986463>",
    "staff": "<:Discord_Staff:1078015590683390093>",
    "verified_bot": "<:Verified_Bot:1078090782118002719>",
    "lastfm": "<:lastfm:1080282189100482693>",
    "steam": "<:steam:1080281878847832186>",
    "contributor": "<:Contributor:1078661797185335398>"
    }


class Data():
    """Tools to manage the bot's database
    """
    async def load_db(table: str, value: str) -> Optional[dict]:
        """Get a dict of the contents of a database's row

        Args:
            table (str): The name of the db table
            value (str): The column to search from

        Returns:
            Optional[dict]: A dictionary of the contents of that row
        """
        async with aiosqlite.connect(DATABASE_FILE) as conn:
            async with conn.execute(f"SELECT * FROM {table} WHERE user_id = ?", (value,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                columns = [description[0]
                           for description in cursor.description]
                data = dict(zip(columns, row))
        return data

    async def create_tables():
        """Creates the tables if missing
        """
        if not os.path.isfile(DATABASE_FILE):
            async with aiosqlite.connect(DATABASE_FILE) as conn:
                cursor = await conn.cursor()

                await cursor.execute("CREATE TABLE profiles (user_id TEXT, lastfm TEXT, steam TEXT, cake TEXT, follow_list TEXT)")
                await cursor.execute("CREATE TABLE settings (user_id TEXT, private INTEGER DEFAULT 0, levels INTEGER DEFAULT 1, experiments INTEGER DEFAULT 0)")
                await cursor.execute("CREATE TABLE rep (user_id INTEGER, rep INTEGER, time INTEGER)")

                await conn.commit()
