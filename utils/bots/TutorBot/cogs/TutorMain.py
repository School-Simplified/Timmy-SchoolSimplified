import discord
from core import database
from core.common import Others
from discord.ext import commands
from datetime import datetime
from discord import slash_command
from discord.commands import permissions
from core.common import MAIN_ID, TUT_ID
import pytz


class TutorMain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RepeatEmoji = {False: "\U00002b1b", True: "🔁"}
        self.ExpireEmoji = {False: "", True: "| ⚠️"}

    @slash_command(name="view", guild_ids=[MAIN_ID.g_main, TUT_ID.g_tut])
    async def view(self, ctx, id=None):
        if id is None:
            query: database.TutorBot_Sessions = (
                database.TutorBot_Sessions.select().where(
                    database.TutorBot_Sessions.TutorID == ctx.author.id
                )
            )

            embed = discord.Embed(
                title="Scheduled Tutor Sessions", color=discord.Color.dark_blue()
            )
            embed.add_field(name="Schedule:", value=f"{ctx.author.name}'s Schedule:")

            if query.count() == 0:
                embed.add_field(
                    name="List:", value="You have no tutor sessions yet!", inline=False
                )

            else:
                list_ten = []
                i = 0
                for entry in query:
                    if not isinstance(entry.Date, datetime):
                        entry.Date = datetime.fromisoformat(entry.Date)
                    datetime_session = pytz.timezone("America/New_York").localize(
                        entry.Date
                    )
                    timestamp = int(datetime.timestamp(datetime_session))

                    student_user = await self.bot.fetch_user(entry.StudentID)
                    list_ten.append(
                        f"{self.RepeatEmoji[entry.Repeat]} `{entry.SessionID}`- - <t:{timestamp}:F> -> "
                        f"{student_user.name} {self.ExpireEmoji[entry.GracePeriod_Status]} "
                    )

                embed.add_field(name="List:", value="\n".join(list_ten), inline=False)
            embed.set_thumbnail(url=Others.timmyTeacher_png)
            embed.set_footer(
                text="Tutor Sessions have a 10 minute grace period before they get deleted, you can find "
                "these sessions with a warning sign next to them."
            )
            try:
                await ctx.respond(embed=embed)
            except:
                await ctx.send(embed=embed)
        else:
            entry = database.TutorBot_Sessions.select().where(
                database.TutorBot_Sessions.SessionID == id
            )
            if entry.exists():
                entry = entry.get()

                student_user = await self.bot.fetch_user(entry.StudentID)
                datetime_session = pytz.timezone("America/New_York").localize(
                    entry.Date
                )
                timestamp = int(datetime.timestamp(datetime_session))

                embed = discord.Embed(
                    title="Tutor Session Query",
                    description=f"Here are the query results for {id}",
                )
                embed.add_field(
                    name="Values",
                    value=f"**Session ID:** `{entry.SessionID}`"
                    f"\n**Student:** `{student_user.name}`"
                    f"\n**Tutor:** `{ctx.author.name}`"
                    f"\n**Date:** <t:{timestamp}:d>"
                    f"\n**Time:** <t:{timestamp}:t>"
                    f"\n**Repeat?:** {self.RepeatEmoji[entry.Repeat]}",
                )
                embed.set_footer(text=f"Subject: {entry.Subject}")
                try:
                    await ctx.respond(embed=embed)
                except:
                    await ctx.send(embed=embed)
            else:
                embed = discord.Embed(
                    title="Invalid Session",
                    description="This session does not exist, please check the ID you've provided!",
                    color=discord.Color.red(),
                )
                try:
                    await ctx.respond(embed=embed)
                except:
                    await ctx.send(embed=embed)

    @slash_command(
        name="mview",  # TODO find better name later
        description="View someone else's tutor sessions",
        guild_ids=[MAIN_ID.g_main, TUT_ID.g_tut],
    )
    @permissions.has_any_role("Senior Tutor", "Tutoring Manager", "Tutoring Director")
    async def mview(self, ctx, user: discord.User):
        query: database.TutorBot_Sessions = database.TutorBot_Sessions.select().where(
            database.TutorBot_Sessions.TutorID == user.id
        )

        embed = discord.Embed(
            title="Scheduled Tutor Sessions", color=discord.Color.dark_blue()
        )
        embed.add_field(name="Schedule:", value=f"{user.name}'s Schedule:")

        if query.count() == 0:
            embed.add_field(
                name="List:", value="This user has no tutor sessions yet!", inline=False
            )

        else:
            list_ten = []
            i = 0
            for entry in query:

                if not isinstance(entry.Date, datetime):
                    entry.Date = datetime.fromisoformat(entry.Date)
                datetime_session = pytz.timezone("America/New_York").localize(
                    entry.Date
                )
                timestamp = int(datetime.timestamp(datetime_session))

                student_user = await self.bot.fetch_user(entry.StudentID)
                list_ten.append(
                    f"{self.RepeatEmoji[entry.Repeat]} `{entry.SessionID}`- - <t:{timestamp}:F> -> {student_user.name} "
                    f"{self.ExpireEmoji[entry.GracePeriod_Status]}"
                )

            embed.add_field(name="List:", value="\n".join(list_ten), inline=False)
        embed.set_thumbnail(url=Others.timmyTeacher_png)

        embed.set_footer(
            text="Tutor Sessions have a 10 minute grace period before they get deleted, you can find "
            "these sessions with a warning sign next to them."
        )
        await ctx.respond(embed=embed)


def setup(bot):
    bot.add_cog(TutorMain(bot))
