import random
import string
from datetime import datetime, timedelta, timezone

import discord
import pytz
from core import database
from core.common import MAIN_ID, TUT_ID
from discord.ext import commands
from discord import Option, slash_command, permissions


async def id_generator(size=3, chars=string.ascii_uppercase):
    while True:
        ID = "".join(random.choice(chars) for _ in range(size))
        query = database.TutorBot_Sessions.select().where(
            database.TutorBot_Sessions.SessionID == ID
        )

        if query.exists():
            continue
        else:
            return ID


class TutorBotStaffCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.est = pytz.timezone("US/Eastern")

    @slash_command(
        name="schedule",
        description="Create a Tutor Session",
        guild_ids=[MAIN_ID.g_main],
    )  # SLASH CMD FOR MAIN SERVER
    @permissions.has_any_role("Tutor")
    async def schedule(
            self,
            ctx,
            date: Option(str, "Enter a date in MM/DD format. EX: 02/02"),
            time: Option(str, "Enter a time in HH:MM format. EX: 3:00"),
            ampm: Option(str, "AM or PM", choices=["AM", "PM"]),
            student: Option(discord.User, "Enter the student you'll be tutoring for this session."),
            subject: Option(str, "Tutoring Subject"),
            repeats: Option(bool, "Does your Tutoring Session repeat?"),
    ):
        embed = discord.Embed(
            title="Schedule Confirmed",
            description="Created session.",
            color=discord.Color.green(),
        )
        now = datetime.now()
        now: datetime = now.astimezone(pytz.timezone("US/Eastern"))
        year = now.strftime("%Y")

        datetimeSession = datetime.strptime(
            f"{date}/{year} {time} {ampm.upper()}", "%m/%d/%Y %I:%M %p"
        )
        datetimeSession = pytz.timezone("America/New_York").localize(datetimeSession)

        if datetimeSession >= now:
            SessionID = await id_generator()

            daterev = datetimeSession.strftime("%m/%d")

            embed.add_field(
                name="Values",
                value=f"**Session ID:** `{SessionID}`\n**Student:** `{student.name}`\n**Tutor:** `{ctx.author.name}`\n"
                      f"**Date:** `{daterev}`\n**Time:** `{time}`\n**Repeat?:** `{repeats}`",
            )
            embed.set_footer(text=f"Subject: {subject}")
            query = database.TutorBot_Sessions.create(
                SessionID=SessionID,
                Date=datetimeSession,
                Time=time,
                StudentID=student.id,
                TutorID=ctx.author.id,
                Repeat=repeats,
                Subject=subject,
                ReminderSet=False,
            )
            query.save()
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="Failed to Generate Session",
                description=f"Unfortunately this session appears to be in the past and Timmy does not support expired "
                            f"sessions.",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed)

    @slash_command(
        name="schedule",
        description="Create a Tutor Session",
        guild_ids=[TUT_ID.g_tut],
    )  # SLASH CMD FOR TUTOR SERVER
    async def _schedule__(
            self,
            ctx,
            date: Option(str, "Enter a date in MM/DD format. EX: 02/02"),
            time: Option(str, "Enter a time in HH:MM format. EX: 3:00"),
            ampm: Option(str, "AM or PM", choices=["AM", "PM"]),
            student: Option(int, "Enter the student ID you'll be tutoring for this session."),
            subject: Option(str, "Tutoring Subject"),
            repeats: Option(bool, "Does your Tutoring Session repeat?"),
    ):
        embed = discord.Embed(
            title="Schedule Confirmed",
            description="Created session.",
            color=discord.Color.green(),
        )
        now = datetime.now()
        now: datetime = now.astimezone(pytz.timezone("US/Eastern"))
        year = now.strftime("%Y")

        datetimeSession = datetime.strptime(
            f"{date}/{year} {time} {ampm.upper()}", "%m/%d/%Y %I:%M %p"
        )
        datetimeSession = pytz.timezone("America/New_York").localize(datetimeSession)

        if datetimeSession >= now:
            SessionID = await id_generator()

            daterev = datetimeSession.strftime("%m/%d")

            embed.add_field(
                name="Values",
                value=f"**Session ID:** `{SessionID}`\n**Student:** `{student.name}`\n**Tutor:** `{ctx.author.name}`\n"
                      f"**Date:** `{daterev}`\n**Time:** `{time}`\n**Repeat?:** `{repeats}`",
            )
            embed.set_footer(text=f"Subject: {subject}")
            query = database.TutorBot_Sessions.create(
                SessionID=SessionID,
                Date=datetimeSession,
                Time=time,
                StudentID=student,
                TutorID=ctx.author.id,
                Repeat=repeats,
                Subject=subject,
                ReminderSet=False,
            )
            query.save()
            await ctx.respond(embed=embed)
        else:
            embed = discord.Embed(
                title="Failed to Generate Session",
                description=f"Unfortunately this session appears to be in the past and Timmy does not support expired "
                            f"sessions.",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed)

    @slash_command(
        name="skip",
        description="Skip a tutoring session",
        guild_ids=[MAIN_ID.g_main, TUT_ID.g_tut]
    )
<<<<<<< HEAD
    #@permissions.has_any_role("Tutor")
=======
    @permissions.has_any_role("Tutor", guild_id=MAIN_ID.g_main)
>>>>>>> beta
    async def skip(self, ctx, id):
        query: database.TutorBot_Sessions = database.TutorBot_Sessions.select().where(
            database.TutorBot_Sessions.SessionID == id
        )
        if query.exists():
            query = query.get()

            old = query.Date
            new = timedelta(days=7)
            nextweek = old + new

            nw = nextweek.strftime("%m/%d/%Y")

            query.Date = nextweek
            query.save()

            await ctx.respond(f"Re-scheduled Session to `{nw}`")

        else:
            embed = discord.Embed(
                title="Invalid Session",
                description="This session does not exist, please check the ID you've provided!",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed)

    @slash_command(
        name="remove",
        description="Remove a tutoring session",
        guild_ids=[MAIN_ID.g_main, TUT_ID.g_tut]
    )
<<<<<<< HEAD
    #@permissions.has_any_role("Tutor")
=======
    @permissions.has_any_role("Tutor", guild_id=MAIN_ID.g_main)
>>>>>>> beta
    async def remove(self, ctx, id):
        query = database.TutorBot_Sessions.select().where(
            database.TutorBot_Sessions.SessionID == id
        )
        if query.exists():
            query = query.get()
            query.delete_instance()

            embed = discord.Embed(
                title="Removed Session",
                description="Deleted Session Successfully",
                color=discord.Color.red(),
            )
            embed.add_field(
                name="Session Removed:",
                value=f"**Session ID:** `{query.SessionID}`"
                f"\n**Student ID:** `{query.StudentID}`",
            )
            await ctx.respond(embed=embed)

        else:
            embed = discord.Embed(
                title="Invalid Session",
                description="This session does not exist, please check the ID you've provided!",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed)

    @slash_command(
        name="clear",
        description="Clear a tutoring session",
        guild_ids=[MAIN_ID.g_main, TUT_ID.g_tut]
    )
<<<<<<< HEAD
    #@permissions.has_any_role("Tutor")
=======
    @permissions.has_any_role("Tutor", guild_id=MAIN_ID.g_main)
>>>>>>> beta
    async def clear(self, ctx):
        query = database.TutorBot_Sessions.select().where(
            database.TutorBot_Sessions.TutorID == ctx.author.id
        )
        var = query.count()
        if var == 0:
            await ctx.respond("You don't have any tutor sessions!")
        else:
            for session in query:
                session.delete_instance()
            await ctx.respond(
                f"All sessions have been deleted!" f"\nDeleted {var} sessions."
            )


def setup(bot):
    bot.add_cog(TutorBotStaffCMD(bot))
