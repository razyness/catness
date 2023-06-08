import struct

import aiohttp
import discord
import aiosqlite
import calendar

from datetime import datetime
from discord import app_commands
from discord.ext import commands

from data import config, Data, icons, DATABASE_FILE


class DownloadButton(discord.ui.View):

    def __init__(self):
        super().__init__()
        self.value = None


class RemoveView(discord.ui.View):
    def __init__(self, user, author):
        super().__init__()
        self.value = None
        self.user = user
        self.author = author

    async def remove_birthday(self, user, author):
        userdata = await Data.load_db(table="profiles", id=author.id, columns=['follow_list', 'following'])
        selfuserdata = await Data.load_db(table="profiles", id=user.id, columns=['follow_list', 'following'])

        user_follow_list = [] if not selfuserdata['following'] else eval(
            selfuserdata['following'])

        self_following = [] if not userdata['follow_list'] else eval(
            userdata['follow_list'])

        if user.id in self_following and author.id in user_follow_list:
            self_following.remove(user.id)
            user_follow_list.remove(author.id)

            await Data.commit_db("UPDATE profiles SET following=? WHERE id=?", (str(self_following), user.id))
            await Data.commit_db("UPDATE profiles SET follow_list=? WHERE id=?", (str(user_follow_list), author.id))

    @discord.ui.button(label="Cancel", emoji=icons.remove, style=discord.ButtonStyle.red)
    async def remove_cake(self, inter, button):
        await self.remove_birthday(self.user, self.author)
        await inter.response.send_message(f"You will not be notified on {self.user.mention}'s birthday", ephemeral=True)


class ProfileView(discord.ui.View):

    def __init__(self, user):
        super().__init__()
        self.value = None
        self.user = user

    async def disable_all(self):
        for i in self.children:
            i.disabled = True
        await self.msg.edit(view=self)

    async def on_timeout(self):
        await self.disable_all()

    async def notify_action(self, user):
        selfuserdata = await Data.load_db(table="profiles", id=self.user.id, columns=['follow_list', 'following'])
        userdata = await Data.load_db(table="profiles", id=user.id, columns=['follow_list', 'following'])

        self_following = [] if not selfuserdata['following'] else eval(
            selfuserdata['following'])
        user_follow_list = [] if not userdata['follow_list'] else eval(
            userdata['follow_list'])

        if user.id not in self_following and self.user.id not in user_follow_list:
            user_follow_list.append(self.user.id)
            self_following.append(user.id)
            await Data.commit_db("UPDATE profiles SET following=? WHERE id=?", (str(self_following), self.user.id))
            await Data.commit_db("UPDATE profiles SET follow_list=? WHERE id=?", (str(user_follow_list), user.id))

            return f"You are now following {self.user.mention}'s birthday!"
        else:
            return f"You are already following {self.user.mention}'s birthday!"

    @discord.ui.button(label="Notify me!", emoji="🎂", style=discord.ButtonStyle.blurple)
    async def notify(self, inter, button):
        resp = await self.notify_action(inter.user)
        view = RemoveView(self.user, inter.user)
        await inter.response.send_message(resp, view=view, ephemeral=True)

    async def interaction_check(self, interaction) -> bool:
        if interaction.user.id == self.user.id:
            await interaction.response.send_message("You can't follow your own birthday, you should remember it i think", ephemeral=True)
            return False
        return True


token = config["TOKEN"]
app = token


def stamp(snowflake_id):
    snowflake_struct = struct.unpack(
        '>Q', snowflake_id.to_bytes(8, byteorder='big'))[0]
    timestamp = (snowflake_struct >> 22) + 1420070400000
    return int(timestamp / 1000)


statuscodes = [
    '100', '101', '102', '200', '201', '202', '203', '204', '206', '207', '300', '301', '302', '303', '304', '305',
    '307', '308', '400', '401', '402', '403', '404', '405', '406', '407', '408', '409', '410', '411', '412', '413',
    '414', '415', '416', '417', '418', '420', '422', '423', '424', '425', '426', '429', '431', '444', '450', '451',
    '497', '498', '499', '500', '501', '502', '503', '504', '506', '507', '508', '509', '510', '511', '521', '522',
    '523', '525', '599']


class DiscordID(commands.Cog):
    def __init__(self, ce) -> None:
        super().__init__()
        self.ce = ce

    @app_commands.command(name="profile", description="View anyone's profile from their id")
    @app_commands.describe(user="Hello pick a user or leave empty for yourself")
    async def discord_id(self, interaction, user: str = None):
        if user is None:
            user = interaction.user.id
        elif user.startswith("<@"):
            user = int(user[2:-1])
        else:
            try:
                user = int(user)
            except:
                await interaction.response.send_message("The id is not valid", ephemeral=True)
                return

        real_user = await self.ce.fetch_user(user)
        url = f"https://discord.com/api/v9/users/{user}"
        headers = {"Authorization": f"Bot {app}"}

        async with aiohttp.ClientSession() as session:
            response = await session.get(url, headers=headers)
            if response.status != 200:
                await interaction.response.send_message(f"https://http.cat/{response.status_code}.jpg",
                                                        ephemeral=True)
                return
            data = await response.json()
            embed = discord.Embed(
                title=f"{data['username']}#{data['discriminator']}",
                url=f"https://discord.com/users/{user}")
            ext = "png"
            if data["avatar"].startswith("a_"):
                ext = "gif"
            embed.set_thumbnail(
                url=f"https://cdn.discordapp.com/avatars/{user}/{data['avatar']}.{ext}?size=4096")
            if data["accent_color"] is not None:
                embed.color = data["accent_color"]
            if data["banner"] is not None:
                ext = "png"
                if data["banner"].startswith("a_"):
                    ext = "gif"
                embed.set_image(
                    url=f"https://cdn.discordapp.com/banners/{user}/{data['banner']}.{ext}?size=4096")
            embed.add_field(name="Public flags",
                            value=data["public_flags"])
            embed.add_field(name="Creation date",
                            value=f"<t:{stamp(int(user))}:R>")
            badges_list = []
            for flag in real_user.public_flags.all():
                badges_list.append(icons[flag.name])
            if data["avatar"].startswith("a_") or data["banner"] is not None:
                badges_list.append(icons.nitro)
            if real_user.bot:
                badges_list.append(icons.bot)
            if real_user.id in config["contributors"]:
                badges_list.append(icons.contributor)
            if real_user.id in config["special"]:
                badges_list.append(icons.special)

            # if user == 912091795318517821:
            #    badges_list = []
            # for icon in icons:
            #    badges_list.append(icons[icon])
            # badges_list.append("<:nitro:1078094211351584928>")
            # badges_list.append("<:bot:1078091845051088979>")

            result = ' '.join(badges_list)
            embed.description = result
            view = DownloadButton()
            if real_user.bot:
                await interaction.response.send_message(embed=embed, view=view)
                view.msg = await interaction.original_response()
                return

            profiles = []

            async with aiosqlite.connect('data/data.db') as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("SELECT * FROM profiles WHERE id = ?", (user,))
                social_data = await cursor.fetchone()

            if social_data:
                for handle_type in ['lastfm', 'steam']:
                    handle_value = social_data[handle_type]
                    if handle_value is not None:
                        profiles.append(
                            f"{icons[handle_type]} `{handle_value}`")
                result = '\n'.join(profiles)

                if profiles != []:
                    embed.add_field(name="Linked profiles",
                                    value=result, inline=True)

                date_str = social_data['cake']
                if date_str is not None:
                    date, consider_age = date_str.split(':')
                    try:
                        if consider_age == "True":
                            formatted_date = f"<t:{int(datetime.strptime(date, '%d/%m/%Y').timestamp())}:D>"
                        else:
                            day, month, _ = date.split("/")
                            month = calendar.month_name[int(month)]
                            formatted_date = f"`{day} {month}`"
                    except:
                        formatted_date = f"`{date}`"
                    view = ProfileView(user=await self.ce.fetch_user(user))
                    embed.add_field(name="Birthday", value=formatted_date)

            ruser = await Data.load_db(table="rep", id=user)

            if ruser is None:
                rep = 0
            else:
                rep = ruser["rep"]

            embed.add_field(name="Rep nepnep",
                            value=f"`{rep}` points", inline=True)

            view.add_item(discord.ui.Button(label='Avatar', style=discord.ButtonStyle.link, url=f"https://cdn.discordapp.com/avatars/{user}/{data['avatar']}.{ext}?size=4096",
                                            emoji=icons.download))
            if data["banner"] is not None:
                view.add_item(discord.ui.Button(label='Banner', style=discord.ButtonStyle.link, url=f"https://cdn.discordapp.com/banners/{user}/{data['banner']}.{ext}?size=4096",
                                                emoji=icons.download))

            settings = await Data.load_db(table="settings", id=user)

            if not real_user.bot and not settings:
                async with aiosqlite.connect(DATABASE_FILE) as db:
                    await db.execute(f"INSERT INTO settings (id) VALUES (?)", (user,))
                    await db.commit()
                settings = await Data.load_db(table="settings", id=user)

            if settings["levels"] == 1:
                levels_info = await Data.load_db(table="profiles", id=user, columns=["level", "exp"])
                level, exp = levels_info["level"], levels_info["exp"]
                missing = round(5 * (level ** 2) + (50 * level) + 100)
                embed.add_field(
                    name="Ranking", value=f"Level `{level}` | `{exp}/{missing}`xp")
            await interaction.response.send_message(embed=embed, view=view)
            view.msg = await interaction.original_response()


async def setup(ce):
    await ce.add_cog(DiscordID(ce))
