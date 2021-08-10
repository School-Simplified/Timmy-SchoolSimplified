import random
import string
from datetime import datetime

import discord
from core import database
from discord.ext import commands, tasks


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

    @commands.command()
    async def skip(self, ctx, id):
        query = database.TutorBot_Sessions.select().where(database.TutorBot_Sessions.SessionID == id)
        if query.exists():
            query = query.get()


            old = query.Date
            new = datetime.timedelta(days=7)
            nextweek = old + new

            nw = nextweek.strftime("%-m/%-d/%Y")

            query.date = nextweek
            query.save()

            await ctx.send(f"Re-scheduled Session to {nw}")

        else:
            embed = discord.Embed(title = "Invalid Session", description = "This session does not exist, please check the ID you've provided!", color = discord.Color.red())
            await ctx.send(embed = embed)


    @commands.command()
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
    async def schedule(self, ctx, date, time, student: discord.User, subject, repeats: bool):
        embed = discord.Embed(title = "Confirm Schedule", description = "Please react with the appropriate reaction to verify this is your schedule.", color = discord.Color.green())

        now = datetime.utcnow()
        year = now.strftime("%Y")

        datetimeSession = datetime.strptime(f"{date}/{year}", "%-m/%-d/%Y")

        SessionID = await id_generator()

        embed.add_field(name = "Values", value = f"**Session ID:** `{SessionID}`\n**Student:** `{student.name}`\n**Tutor:** `{ctx.author.name}`\n**Date:** `{date}`\n**Time:** `{time}`\n**Repeat?:** `{repeats}`")
        embed.set_footer(text = f"Subject: {subject}")
        query = database.TutorBot_Sessions.create(SessionID = SessionID, Date = datetimeSession, time = time, StudentID = id, TutorID = ctx.author.id, Repeat = repeats, Subject = subject)
        query.save()
        
        
        await ctx.send(embed = embed)

def setup(bot):
    bot.add_cog(TutorBotStaffCMD(bot))


