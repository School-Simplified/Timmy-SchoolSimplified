import random
import string
from datetime import datetime, timedelta, timezone

import discord
import pytz
from core import database
from core.common import MAIN_ID
from discord.ext import commands


async def id_generator(size=3, chars=string.ascii_uppercase):
    while True:
        ID = ''.join(random.choice(chars) for _ in range(size))
        query = database.TutorBot_Sessions.select().where(database.TutorBot_Sessions.SessionID == ID)

        if query.exists():
            continue
        else:
            return ID


class TutorBotStaffCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.est = pytz.timezone('US/Eastern')

    @commands.command()
    @commands.has_role("Tutor")
    async def skip(self, ctx, id):
        query: database.TutorBot_Sessions = database.TutorBot_Sessions.select().where(database.TutorBot_Sessions.SessionID == id)
        if query.exists():
            query = query.get()

            old = query.Date
            new = timedelta(days=7)
            nextweek = old + new

            nw = nextweek.strftime("%m/%d/%Y")

            query.Date = nextweek
            query.save()

            await ctx.send(f"Re-scheduled Session to `{nw}`")

        else:
            embed = discord.Embed(title = "Invalid Session",
                                  description = "This session does not exist, please check the ID you've provided!",
                                  color = discord.Color.red())
            await ctx.send(embed = embed)


    @commands.command()
    @commands.has_role("Tutor")
    async def remove(self, ctx, id):
        query = database.TutorBot_Sessions.select().where(database.TutorBot_Sessions.SessionID == id)
        if query.exists():
            query = query.get()
            query.delete_instance()
            
            embed = discord.Embed(title= "Removed Session", description = "Deleted Session Successfully", color = discord.Color.red())
            embed.add_field(name = "Session Removed:", value = f"**Session ID:** `{query.SessionID}`"
                                                               f"\n**Student ID:** `{query.StudentID}`")
            await ctx.send(embed = embed)

        else:
            embed = discord.Embed(title = "Invalid Session", description = "This session does not exist, please check the ID you've provided!",
                                  color = discord.Color.red())
            await ctx.send(embed = embed)


    @commands.command()
    @commands.has_role("Tutor")
    async def schedule(self, ctx, date, time, ampm:str, student: discord.User, subject, repeats: bool = False):
        if ctx.guild.id != MAIN_ID.g_main:
            await ctx.send("Woah! Looks like you aren't using the new slash command! In the future, "
                           "this command will be removed so please use the slash command instead!"
                           "\nYou can do this by clicking `/` in the chat bar and selecting the `schedule` command from Timmy. ")
        embed = discord.Embed(title = "Schedule Confirmed", description = "Created session.", color = discord.Color.green())
        now = datetime.now()
        now :datetime = now.astimezone(self.est)
        year = now.strftime("%Y")

        datetimeSession = datetime.strptime(f"{date}/{year} {time} {ampm.upper()}", "%m/%d/%Y %I:%M %p")
        datetimeSession = pytz.timezone("America/New_York").localize(datetimeSession)

        if datetimeSession >= now:
            SessionID = await id_generator()

            daterev = datetimeSession.strftime("%m/%d")

            embed.add_field(name = "Values", value = f"**Session ID:** `{SessionID}`"
                                                     f"\n**Student:** `{student.name}`"
                                                     f"\n**Tutor:** `{ctx.author.name}`"
                                                     f"\n**Date:** `{daterev}`"
                                                     f"\n**Time:** `{time}`"
                                                     f"\n**Repeat?:** `{repeats}`")
            embed.set_footer(text = f"Subject: {subject}")
            query = database.TutorBot_Sessions.create(SessionID = SessionID, Date = datetimeSession,
                                                      Time = time, StudentID = student.id, TutorID = ctx.author.id,
                                                      Repeat = repeats, Subject = subject, ReminderSet = False)
            query.save()
            await ctx.send(embed = embed)
        else:
            embed = discord.Embed(title = "Failed to Generate Session",
                                  description = f"Unfortunately this session appears to be in the past and Timmy does "
                                                f"not support expired sessions.",
                                  color = discord.Color.red())
            await ctx.send(embed = embed)


    @commands.command()
    @commands.has_role("Tutor")
    async def clear(self, ctx):
        query = database.TutorBot_Sessions.select().where(database.TutorBot_Sessions.TutorID == ctx.author.id)
        var = query.count()
        if var == 0:
            await ctx.send("You don't have any tutor sessions!")
        else:
            for session in query:
                session.delete_instance()
            await ctx.send(f"All sessions have been deleted!"
                           f"\nDeleted {var} sessions.")


def setup(bot):
    bot.add_cog(TutorBotStaffCMD(bot))


