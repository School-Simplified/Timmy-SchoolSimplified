import random
import string
from datetime import datetime, timedelta, timezone

import discord
import pytz
from core import database
from core.common import MAIN_ID, TUT_ID
from discord.ext import commands
from discord import slash_command, permissions


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
        name="skip",
        description="Skip a tutoring session",
        guild_ids=[MAIN_ID.g_main, TUT_ID.g_tut]
    )
    @permissions.has_any_role("Tutor", guild_id=MAIN_ID.g_main)
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
    @permissions.has_any_role("Tutor", guild_id=MAIN_ID.g_main)
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
    @permissions.has_any_role("Tutor", guild_id=MAIN_ID.g_main)
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
