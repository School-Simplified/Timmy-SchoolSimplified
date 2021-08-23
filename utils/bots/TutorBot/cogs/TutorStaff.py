import random
import string
from datetime import datetime, timedelta, timezone

import discord
import pytz
from core import database
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
            embed = discord.Embed(title = "Invalid Session", description = "This session does not exist, please check the ID you've provided!", color = discord.Color.red())
            await ctx.send(embed = embed)


    @commands.command()
    @commands.has_role("Tutor")
    async def remove(self, ctx, id):
        query = database.TutorBot_Sessions.select().where(database.TutorBot_Sessions.SessionID == id)
        if query.exists():
            query = query.get()
            query.delete_instance()
            
            embed = discord.Embed(title= "Removed Session", description = "Deleted Session Successfully", color = discord.Color.red())
            embed.add_field(name = "Session Removed:", value = f"**Session ID:** `{query.SessionID}`\n**Student ID:** `{query.StudentID}`")
            await ctx.send(embed = embed)

        else:
            embed = discord.Embed(title = "Invalid Session", description = "This session does not exist, please check the ID you've provided!", color = discord.Color.red())
            await ctx.send(embed = embed)

    @commands.command()
    @commands.has_role("Tutor")
    async def schedule(self, ctx, date, time, ampm:str, student: discord.User, subject, repeats: bool = False):
        embed = discord.Embed(title = "Schedule Confirmed", description = "Created session.", color = discord.Color.green())
        now = datetime.now()
        now :datetime = now.astimezone(self.est)
        year = now.strftime("%Y")

        datetimeSession = datetime.strptime(f"{date}/{year} {time} {ampm.upper()}", "%m/%d/%Y %I:%M %p")
        datetimeSession = pytz.timezone("America/New_York").localize(datetimeSession)

        if datetimeSession >= now:
            SessionID = await id_generator()

            daterev = datetimeSession.strftime("%m/%d")

            embed.add_field(name = "Values", value = f"**Session ID:** `{SessionID}`\n**Student:** `{student.name}`\n**Tutor:** `{ctx.author.name}`\n**Date:** `{daterev}`\n**Time:** `{time}`\n**Repeat?:** `{repeats}`")
            embed.set_footer(text = f"Subject: {subject}")
            query = database.TutorBot_Sessions.create(SessionID = SessionID, Date = datetimeSession, Time = time, StudentID = student.id, TutorID = ctx.author.id, Repeat = repeats, Subject = subject, ReminderSet = False)
            query.save()
            await ctx.send(embed = embed)
        else:
            embed = discord.Embed(title = "Failed to Generate Session", description = f"Unfortunately this session appears to be in the past and Timmy does not support expired sessions.", color = discord.Color.red())
            await ctx.send(embed = embed)

    @schedule.error
    async def schedule_error(self, ctx, error):
        if isinstance(error, (commands.UserNotFound, commands.errors.UserNotFound)):
            em = discord.Embed(title = "Bad Argument!", description = "Looks like you messed up an argument somewhere here!\n\n**Check the following:**\n-> If you seperated the time and the AM/PM. (Eg; 5:00 PM)\n-> If you provided a valid student's ID\n-> If you followed the MM/DD Format.\n-> Keep all the arguments in one word.\n-> If you followed the [documentation for schedule.](https://timmy.schoolsimplified.org/tutorbot#schedule)", color = 0xf5160a)
            em.set_thumbnail(url = "https://icons.iconarchive.com/icons/paomedia/small-n-flat/1024/sign-error-icon.png")
            em.set_footer(text = "Consult the Help Command if you are having trouble or call over a Bot Manager!")
            await ctx.send(embed = em)
        
        elif isinstance(error, (commands.MissingRequiredArgument, commands.errors.MissingRequiredArgument)):
            em = discord.Embed(title = "Bad Argument!", description = "Looks like you messed up an argument somewhere here!\n\n**Check the following:**\n-> If you seperated the time and the AM/PM. (Eg; 5:00 PM)\n-> If you provided a valid student's ID\n-> If you followed the MM/DD Format.\n-> Keep all the arguments in one word.\n-> If you followed the [documentation for schedule.](https://timmy.schoolsimplified.org/tutorbot#schedule)", color = 0xf5160a)
            em.set_thumbnail(url = "https://icons.iconarchive.com/icons/paomedia/small-n-flat/1024/sign-error-icon.png")
            em.set_footer(text = "Consult the Help Command if you are having trouble or call over a Bot Manager!")
            await ctx.send(embed = em)
        else:
            raise error
            
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
            await ctx.send(f"All sessions have been deleted!\nDeleted {var} sessions.")

def setup(bot):
    bot.add_cog(TutorBotStaffCMD(bot))


