from datetime import datetime, timedelta

import discord
import pytz
from discord.ext import commands, tasks

from core import database
from core.common import TutID
from core.logging_module import get_log

_log = get_log(__name__)


class TutorBotLoop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.est = pytz.timezone("US/Eastern")
        self.tutorsession_graceperiod.start()

    async def cog_unload(self):
        self.tutorsession.cancel()
        self.tutorsession_graceperiod.cancel()

    @tasks.loop(seconds=60.0)
    async def tutorsession(self):
        now = datetime.now(self.est)
        for entry in database.TutorBot_Sessions:
            TutorSession = pytz.timezone("America/New_York").localize(entry.Date)
            val = int((TutorSession - now).total_seconds())

            if 120 >= val >= 1:
                tutor = self.bot.get_user(entry.TutorID)
                student = self.bot.get_user(entry.StudentID)

                if tutor is None:
                    tutor = self.bot.get_user(entry.TutorID)
                if student is None:
                    student = self.bot.get_user(entry.StudentID)

                botch = self.bot.get_channel(TutID.ch_bot_commands)
                embed = discord.Embed(
                    title="ALERT: You have a Tutor Session Soon!",
                    description="Please make sure you both communicate and set up a private voice channel!",
                    color=discord.Color.green(),
                )
                embed.add_field(
                    name="Tutor Session Details",
                    value=f"**Tutor:** {tutor.name}"
                    f"\n**Student:** {student.name}"
                    f"\n**Session ID:** {entry.SessionID}"
                    f"\n**Time:** {entry.Time}",
                )

                try:
                    await tutor.send(embed=embed)
                except:
                    await botch.send(
                        f"Unable to send a reminder DM to you {tutor.mention}!",
                        embed=embed,
                    )
                try:
                    await student.send(embed=embed)
                except:
                    _log.warning(
                        f"TutorLoop: Unable to Send a Reminder DM to: {student.id}"
                    )

                geten: database.TutorBot_Sessions = (
                    database.TutorBot_Sessions.select()
                    .where(database.TutorBot_Sessions.id == entry.id)
                    .get()
                )

                if geten.Repeat:
                    old = geten.Date
                    new = timedelta(days=7)
                    nextweek = old + new
                    geten.Date = nextweek

                geten.ReminderSet = True
                geten.save()

            elif val < 0 and not entry.Repeat:
                geten: database.TutorBot_Sessions = (
                    database.TutorBot_Sessions.select()
                    .where(database.TutorBot_Sessions.id == entry.id)
                    .get()
                )
                old = geten.Date
                new = timedelta(minutes=10.0)
                geten.GracePeriod_Status = True
                geten.save()

                GP_DATE = old + new

                gp_en: database.TutorSession_GracePeriod = (
                    database.TutorSession_GracePeriod.create(
                        SessionID=geten.SessionID,
                        authorID=geten.TutorID,
                        ext_ID=geten.id,
                        GP_DATE=GP_DATE,
                    )
                )
                gp_en.save()
                # geten.delete_instance()

            elif val < 0 and entry.Repeat:
                query: database.TutorBot_Sessions = (
                    database.TutorBot_Sessions.select()
                    .where(database.TutorBot_Sessions.id == entry.id)
                    .get()
                )
                old = query.Date
                new = timedelta(days=7)
                nextweek = old + new

                nw = nextweek.strftime("%m/%d/%Y")

                query.Date = nextweek
                query.save()

    @tasks.loop(seconds=60.0)
    async def tutorsession_graceperiod(self):
        now = datetime.now(self.est)
        for entry in database.TutorSession_GracePeriod:
            TutorSession = pytz.timezone("America/New_York").localize(entry.GP_DATE)
            val = int((TutorSession - now).total_seconds())

            if 120 >= val >= 1:
                try:
                    geten: database.TutorBot_Sessions = (
                        database.TutorBot_Sessions.select()
                        .where(database.TutorBot_Sessions.id == entry.ext_ID)
                        .get()
                    )
                except Exception as e:
                    entry.delete_instance()
                else:
                    geten.delete_instance()
                    entry.delete_instance()

    @tutorsession.before_loop
    async def before_loop_(self):
        await self.bot.wait_until_ready()

    @tutorsession_graceperiod.before_loop
    async def before_loop_(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(TutorBotLoop(bot))
