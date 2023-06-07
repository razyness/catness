from discord import app_commands
from discord.app_commands import Choice
from discord.ext import commands, tasks
from datetime import datetime, timedelta


class RemindObject:
    def __init__(self, id: str, text: str, time: int, unit: str, channel: tuple = None):
        self.id = id
        self.text = text
        self.time = time
        self.unit = unit
        self.channel = channel


class Reminder(commands.Cog):
    def __init__(self, ce: commands.Bot):
        super().__init__()
        self.ce = ce
        self.reminders = {}
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()

    @tasks.loop(seconds=10)
    async def check_reminders(self):
        current_time = datetime.now()
        expired_reminders = []

        for reminder_id, reminder in self.reminders.items():
            reminder_time = datetime.fromtimestamp(reminder.time)
            if reminder_time <= current_time:
                expired_reminders.append(reminder_id)

        for reminder_id in expired_reminders:
            reminder = self.reminders.pop(reminder_id)
            if reminder.channel[0] is False:
                user = self.bot.get_user(int(reminder.channel[1]))
                if user:
                    await user.send(f"Reminder: {reminder.text}")
            else:
                channel = self.bot.get_channel(int(reminder.channel[0]))
                if channel:
                    await channel.send(f"Reminder: {reminder.text}")

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.ce.wait_until_ready()

    group = app_commands.Group(
		name="reminder", description="Reminder things")
    
    @group.command(name="add", description="Set a reminder")
    @app_commands.choices(unit=[
                   Choice(name="Day(s)", value="d"),
                   Choice(name="Hour(s)", value="h"),
                   Choice(name="Minute(s)", value="m")
                   ])
    async def remind(self, inter: commands.Context, task: str, time: int, unit: str = "h", private: bool = False):
        units = {"d": "days", "h": "hours", "m": "minutes"}

        remind_time = datetime.now() + timedelta(**{units[unit]: time})
        remind_obj = RemindObject(str(inter.user.id), task, remind_time.timestamp(), unit, (str(inter.channel.id)) if private else (False, inter.user.id))

        if not private:
            await inter.response.send_message(f"I'll remind you here: `{remind_obj.text}`, <t:{int(remind_obj.time)}:R>")
        else:
            await inter.response.send_message(f"You'll receive a DM: `{remind_obj.text}`, <t:{int(remind_obj.time)}:R>", ephemeral=True)

        self.reminders[remind_obj.id] = remind_obj

    @group.command(name="view", description="View existing reminders")
    async def view_reminders(self, inter: commands.Context):
        if self.reminders:
            reminder_list = "\n".join(f"- `{reminder.text}` | <t:{int(reminder.time)}:R>" for reminder in self.reminders.values())
            await inter.response.send_message(f"Existing Reminders:\n{reminder_list}", ephemeral=True)
        else:
            await inter.response.send_message("There are no reminders set.", ephemeral=True)


async def setup(ce):
    await ce.add_cog(Reminder(ce))
