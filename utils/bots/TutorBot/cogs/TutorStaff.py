import random
import string
from datetime import datetime, timedelta
from typing import Literal

import pytz

import discord
from core import database
from core.common import MAIN_ID, TUT_ID
from discord.app_commands import command, describe, guilds
from discord.ext import commands


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
    )  # SLASH CMD FOR MAIN SERVER
    @guilds(MAIN_ID.g_main)
    # @permissions.has_any_role("Tutor")
    @describe(
        date="Enter a date in MM/DD format. EX: 02/02",
        time="Enter a time in HH:MM format in EST. EX: 3:00",
        ampm="AM or PM",
        student="Enter the student ID you'll be tutoring for this session.",
        repeats="Does your Tutoring Session repeat?",
        subject="Tutoring subject"
    )
    async def schedule(
        self,
        interaction: discord.Interaction,
        date: str,
        time: str,
        ampm: Literal["AM", "PM"],
        student: discord.Member,
        repeats: bool,
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
                f"\n**Tutor:** `{interaction.user.name}`"
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
                TutorID=interaction.user.id,
                Repeat=repeats,
                Subject=subject,
                ReminderSet=False,
            )
            query.save()
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Failed to Generate Session",
                description=f"Unfortunately this session appears to be in the past and Timmy does not support expired "
                f"sessions.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed)

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

    @command(
        name="schedule",
        description="Create a Tutor Session",
    )
    @guilds(TUT_ID.g_tut)
    @describe(
        date="Enter a date in MM/DD format. EX: 02/02",
        time="Enter a time in HH:MM format in EST. EX: 3:00",
        ampm="AM or PM",
        student="Enter the student ID you'll be tutoring for this session.",
        repeats="Does your Tutoring Session repeat?",
        subject="Tutoring subject"
    )
    async def schedule_t(
        self,
        interaction: discord.Interaction,
        date: str,
        time: str,
        ampm: Literal["AM", "PM"],
        student: str,
        repeats: bool,
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
                f"\n**Tutor:** `{interaction.user.name}`"
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
                TutorID=interaction.user.id,
                Repeat=repeats,
                Subject=subject,
                ReminderSet=False,
            )
            query.save()
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Failed to Generate Session",
                description=f"Unfortunately this session appears to be in the past and Timmy does not support expired "
                f"sessions.",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed)

    @command(
        name="skip",
        description="Skip a tutoring session",
    )
    @guilds(MAIN_ID.g_main, TUT_ID.g_tut)
    async def skip(self, interaction: discord.Interaction, id: str):
        query: database.TutorBot_Sessions = database.TutorBot_Sessions.select().where(
            database.TutorBot_Sessions.SessionID == id
        )
        if query.exists():
            query = query.get()
            if query.TutorID == interaction.user.id:

                old = query.Date
                new = timedelta(days=7)
                nextweek = old + new

                nw = nextweek.strftime("%m/%d/%Y")

                query.Date = nextweek
                query.save()

                await interaction.response.send_message(f"Re-scheduled Session to `{nw}`")
            else:
                embed = discord.Embed(
                    title="Invalid Permissions",
                    description="This session does exist, but you are not the owner of it!",
                    color=discord.Color.red(),
                )
                await interaction.response.send_message(embed=embed)

        else:
            embed = discord.Embed(
                title="Invalid Session",
                description="This session does not exist, please check the ID you've provided!",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed)

    @command(
        name="remove",
        description="Remove a tutoring session"
    )
    @guilds(MAIN_ID.g_main, TUT_ID.g_tut)
    async def remove(self, interaction: discord.Interaction, id: str):
        query = database.TutorBot_Sessions.select().where(
            database.TutorBot_Sessions.SessionID == id
        )
        if query.exists():
            query = query.get()
            if query.TutorID == interaction.user.id:
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
                await interaction.response.send_message(embed=embed)
            else:
                embed = discord.Embed(
                    title="Invalid Permissions",
                    description="This session does exist, but you are not the owner of it!",
                    color=discord.Color.red(),
                )
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(
                title="Invalid Session",
                description="This session does not exist, please check the ID you've provided!",
                color=discord.Color.red(),
            )
            await interaction.response.send_message(embed=embed)

    @command(
        name="clear",
        description="Clear a tutoring session",
    )
    @guilds(MAIN_ID.g_main, TUT_ID.g_tut)
    async def clear(self, interaction: discord.Interaction):
        query = database.TutorBot_Sessions.select().where(
            database.TutorBot_Sessions.TutorID == interaction.user.id
        )
        var = query.count()
        if var == 0:
            await interaction.response.send_message("You don't have any tutor sessions!")
        else:
            for session in query:
                session.delete_instance()
            await interaction.response.send_message(
                f"All sessions have been deleted!" f"\nDeleted {var} sessions."
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(TutorBotStaffCMD(bot))
