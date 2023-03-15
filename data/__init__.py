import sqlite3
import aiosqlite
import toml

class Data():
    async def get_social_data():
        async with aiosqlite.connect("data/profiles.db") as conn:
            cursor = conn.cursor()
            await cursor.execute("SELECT user_id, lastfm, steam FROM profiles")
            rows = await cursor.fetchall()
            social_data = {}
            for row in rows:
                user_id, lastfm, steam = row
                social_data[user_id] = {"lastfm": lastfm, "steam": steam}
            return social_data

    

config = toml.load("data/config.toml")
