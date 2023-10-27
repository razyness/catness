from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks

import asyncio
import time as tm
import uuid
import discord


class RemindObject:
    def __init__(self, id: str, task: str, remind_time: int, channel: tuple = None, reminder_id: str = None):
        self.id = id
        self.task = task
        self.remind_time = remind_time
        self.channel = channel
        self.reminder_id = reminder_id or str(uuid.uuid4())


class Reminder(commands.Cog):
    """
    Commands to set, view and edit (soon) your reminders. Up to 5 at a time.
    """

    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.reminders = {}
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()

    async def send_reminder(self, remind_obj, remaining_time: int):
        if remaining_time > 0:
            await asyncio.sleep(remaining_time)

        user = await self.bot.get_or_fetch_user(remind_obj.id)
        if remind_obj.channel[0]:
            if user:
                await user.send(f"Reminder: {remind_obj.task}")
        else:
            channel = self.bot.get_channel(remind_obj.channel[1]) or await self.bot.fetch_channel(remind_obj.channel[1])
            if channel:
                await channel.send(f"{user.mention} reminder: {remind_obj.task}")

        async with self.bot.db_pool.acquire() as conn:
            await conn.execute("DELETE FROM reminders WHERE reminder_id = $1", remind_obj.reminder_id)

    @tasks.loop(seconds=60)
    async def check_reminders(self):
        async with self.bot.db_pool.acquire() as conn:
            reminders = await conn.fetch("SELECT * FROM reminders WHERE remind_time <= $1", int(tm.time() + 60))
            for reminder in reminders:
                remind_obj = RemindObject(
                    id=reminder['id'],
                    task=reminder['task'],
                    remind_time=reminder['remind_time'],
                    channel=(reminder['private'], reminder['channel']),
                    reminder_id=reminder['reminder_id']
                )
                await self.send_reminder(remind_obj, remaining_time=reminder['remind_time'] - int(tm.time()))

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()

    group = app_commands.Group(
        name="reminder", description="Reminder things")

    @group.command(name="add", description="Set a reminder")
    @app_commands.choices(unit=[
        Choice(name="Day(s)", value="d"),
        Choice(name="Hour(s)", value="h"),
        Choice(name="Minute(s)", value="m")
    ])
    async def remind(self, inter: commands.Context, task: str, time: int, unit: str = "h", private: bool = False):
        # i think this is right
        units = {"d": 86400, "h": 3600, "m": 60}

        if inter.guild is None:
            private = True

        reminder_uuid = str(uuid.uuid4())
        remind_time = int(tm.time()) + time * units[unit]

        remind_obj = RemindObject(inter.user.id, task, remind_time, (True, None) if private else (
            False, inter.channel.id), reminder_uuid)

        async with self.bot.db_pool.acquire() as conn:
            async with conn.transaction():
                reminders = await conn.fetch("SELECT * FROM reminders WHERE id = $1", inter.user.id)
                if len(reminders) >= 5:
                    await inter.response.send_message("You have reached the maximum number of reminders (5).", ephemeral=True)
                    return
                await conn.execute("INSERT INTO reminders (id, task, remind_time, private, channel, reminder_id) VALUES ($1, $2, $3, $4, $5, $6)", inter.user.id, task, remind_obj.remind_time, private, str(remind_obj.channel[1]), str(uuid.uuid4()))
                self.reminders[remind_obj.id] = remind_obj

        if not private:
            await inter.response.send_message(f"I'll remind you here: `{remind_obj.task}`, <t:{int(remind_obj.remind_time)}:R>")
        else:
            await inter.response.send_message(f"You'll receive a DM: `{remind_obj.task}`, <t:{int(remind_obj.remind_time)}:R>", ephemeral=True)

    @group.command(name="view", description="View existing reminders")
    async def view_reminders(self, inter: commands.Context):
        async with self.bot.db_pool.acquire() as conn:
            reminders = await conn.fetch("SELECT * FROM reminders WHERE id = $1", inter.user.id)
            if reminders:
                reminder_list = sorted(
                    reminders, key=lambda r: r['remind_time'])
                embed = discord.Embed(
                    title="Existing Reminders")
                for reminder in reminder_list:
                    emoji = "🔒" if reminder['private'] else "#️⃣"
                    task = reminder['task']
                    channel = reminder['channel']
                    embed.add_field(name=f"{emoji} {task}", value=f"Expires <t:{reminder['remind_time']}:R>\n{f'<#{channel}>' if channel.isdigit() else ''}", inline=False)
                
                embed.set_footer(text='🔒 DM reminders, #️⃣ Channel reminders')
                await inter.response.send_message(embed=embed, ephemeral=True)
            else:
                await inter.response.send_message("There are no reminders set.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(Reminder(bot))
