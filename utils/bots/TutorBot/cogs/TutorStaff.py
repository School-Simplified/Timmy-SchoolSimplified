import random
import string
from datetime import datetime, timedelta
import pytz

import discord
from core import database
from core.common import MAIN_ID, TUT_ID
from discord.ext import commands
from discord import Option, slash_command
from discord.commands import permissions


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
        time: Option(str, "Enter a time in HH:MM format in EST. EX: 3:00"),
        ampm: Option(str, "AM or PM", choices=["AM", "PM"]),
        student: Option(
            discord.User, "Enter the student you'll be tutoring for this session."
        ),
        repeats: Option(bool, "Does your Tutoring Session repeat?"),
        subject: Option(str, "Tutoring Subject"),
    ):
        embed = discord.Embed(
            title="Schedule Confirmed",
            description="Created session.",
            color=discord.Color.green(),
        )
        now = datetime.now(tz=pytz.timezone("US/Eastern"))
        year = now.strftime("%Y")

        datetime_session = datetime.strptime(
            f"{date}/{year} {time} {ampm.upper()}", "%m/%d/%Y %I:%M %p"
        )
        datetime_session = pytz.timezone("America/New_York").localize(datetime_session)
        timestamp = int(datetime.timestamp(datetime_session))

        if datetime_session >= now:
            session_id = await id_generator()

            embed.add_field(
                name="Values",
                value=f"**Session ID:** `{session_id}`"
                f"\n**Student:** `{student.name}`"
                f"\n**Tutor:** `{ctx.author.name}`"
                f"\n**Date:** <t:{timestamp}:d>"
                f"\n**Time:** <t:{timestamp}:t>"
                f"\n**Repeat?:** `{repeats}`",
            )
            embed.set_footer(text=f"Subject: {subject}")
            query = database.TutorBot_Sessions.create(
                SessionID=session_id,
                Date=datetime_session,
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

    @commands.command(name="schedule")
    @commands.has_any_role("Tutor")
    async def schedule(
        self,
        ctx,
        date: str,
        time: str,
        ampm: str,
        student: discord.User,
        repeats: bool,
        *,
        subject: str,
    ):
        embed = discord.Embed(
            title="Schedule Confirmed",
            description="Created session.",
            color=discord.Color.green(),
        )
        now = datetime.now(tz=pytz.timezone("US/Eastern"))
        year = now.strftime("%Y")

        datetime_session = datetime.strptime(
            f"{date}/{year} {time} {ampm.upper()}", "%m/%d/%Y %I:%M %p"
        )
        datetime_session = pytz.timezone("America/New_York").localize(datetime_session)
        timestamp = int(datetime.timestamp(datetime_session))

        if datetime_session >= now:
            session_id = await id_generator()

            embed.add_field(
                name="Values",
                value=f"**Session ID:** `{session_id}`"
                f"\n**Student:** `{student.name}`"
                f"\n**Tutor:** `{ctx.author.name}`"
                f"\n**Date:** <t:{timestamp}:d>"
                f"\n**Time:** <t:{timestamp}:t>"
                f"\n**Repeat?:** `{repeats}`",
            )
            embed.set_footer(text=f"Subject: {subject}")
            query = database.TutorBot_Sessions.create(
                SessionID=session_id,
                Date=datetime_session,
                Time=time,
                StudentID=student.id,
                TutorID=ctx.author.id,
                Repeat=repeats,
                Subject=subject,
                ReminderSet=False,
            )
            query.save()
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(
                title="Failed to Generate Session",
                description=f"Unfortunately this session appears to be in the past and Timmy does not support expired "
                f"sessions.",
                color=discord.Color.red(),
            )
            await ctx.send(embed=embed)

    @slash_command(
        name="schedule",
        description="Create a Tutor Session",
        guild_ids=[TUT_ID.g_tut],
    )  # SLASH CMD FOR TUTOR SERVER
    async def schedule_t(
        self,
        ctx,
        date: Option(str, "Enter a date in MM/DD format. EX: 02/02"),
        time: Option(str, "Enter a time in HH:MM format in EST. EX: 3:00"),
        ampm: Option(str, "AM or PM", choices=["AM", "PM"]),
        student: Option(
            str, "Enter the student ID you'll be tutoring for this session."
        ),
        repeats: Option(bool, "Does your Tutoring Session repeat?"),
        subject: Option(str, "Tutoring Subject"),
    ):
        embed = discord.Embed(
            title="Schedule Confirmed",
            description="Created session.",
            color=discord.Color.green(),
        )
        now = datetime.now(tz=pytz.timezone("US/Eastern"))

        year = now.strftime("%Y")

        datetime_session = datetime.strptime(
            f"{date}/{year} {time} {ampm.upper()}",
            "%m/%d/%Y %I:%M %p",
        )

        datetime_session = pytz.timezone("America/New_York").localize(datetime_session)
        timestamp = int(datetime.timestamp(datetime_session))

        student = self.bot.get_user(int(student))

        if datetime_session >= now:
            session_id = await id_generator()

            embed.add_field(
                name="Values",
                value=f"**Session ID:** `{session_id}`"
                f"\n**Student:** `{student.name}`"
                f"\n**Tutor:** `{ctx.author.name}`"
                f"\n**Date:** <t:{timestamp}:d>"
                f"\n**Time:** <t:{timestamp}:t>"
                f"\n**Repeat?:** `{repeats}`",
            )
            embed.set_footer(text=f"Subject: {subject}")
            query = database.TutorBot_Sessions.create(
                SessionID=session_id,
                Date=datetime_session,
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
        name="skip",
        description="Skip a tutoring session",
        guild_ids=[MAIN_ID.g_main, TUT_ID.g_tut],
    )
    async def skip(self, ctx, id: str):
        query: database.TutorBot_Sessions = database.TutorBot_Sessions.select().where(
            database.TutorBot_Sessions.SessionID == id
        )
        if query.exists():
            query = query.get()
            if query.TutorID == ctx.author.id:

                old = query.Date
                new = timedelta(days=7)
                nextweek = old + new

                nw = nextweek.strftime("%m/%d/%Y")

                query.Date = nextweek
                query.save()

                await ctx.respond(f"Re-scheduled Session to `{nw}`")
            else:
                embed = discord.Embed(
                title="Invalid Permissions",
                description="This session does exist, but you are not the owner of it!",
                color=discord.Color.red(),
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
        name="remove",
        description="Remove a tutoring session",
        guild_ids=[MAIN_ID.g_main, TUT_ID.g_tut],
    )
    async def remove(self, ctx, id):
        query = database.TutorBot_Sessions.select().where(
            database.TutorBot_Sessions.SessionID == id
        )
        if query.exists():
            query = query.get()
            if query.TutorID == ctx.author.id:
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
                title="Invalid Permissions",
                description="This session does exist, but you are not the owner of it!",
                color=discord.Color.red(),
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
        guild_ids=[MAIN_ID.g_main, TUT_ID.g_tut],
    )
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
