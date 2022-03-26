import pytz
import datetime
from dateutil import parser
import discord
from discord.ext import tasks, commands

from core.database import StudyVCLeaderboard


class StudyLoop(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.est = pytz.timezone("US/Eastern")
        self.lastReset = parser.parse("14.03.2022 00:00:00 EST", tzinfos={"EST": -4 * 3600})     # 14.03.2022 as default value
        self.midnight = datetime.datetime.strptime("00:00:00", "%H:%M:%S").time()

        self.TTSWeekCheck.start()

    def cog_unload(self):
        self.TTSWeekCheck.stop()

    @tasks.loop(seconds=10)
    async def TTSWeekCheck(self):
        now = datetime.datetime.now(self.est)
        weekdayNow = now.isoweekday()
        timeNow = now.time()

        queryLeaderboard = StudyVCLeaderboard.select()
        entries = [entry.id for entry in queryLeaderboard]

        if weekdayNow == 1 and (now - self.lastReset >= datetime.timedelta(days=7)) and timeNow >= self.midnight:
            lastReset = now
            for entry in entries:
                queryLeaderboard = queryLeaderboard.select().where(StudyVCLeaderboard.id == entry)
                queryLeaderboard = queryLeaderboard.get()
                queryLeaderboard.TTSWeek = 0
                queryLeaderboard.save()


async def setup(bot: commands.Bot):
    await bot.add_cog(StudyLoop(bot))