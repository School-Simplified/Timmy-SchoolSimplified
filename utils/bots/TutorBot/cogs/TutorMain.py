from tkinter import E, Entry

import discord
from core import database
from discord.ext import commands, tasks


class TutorBotStaffCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RepeatEmoji = {
            True: "\U00002b1b",
            False: "🔁"
        }

    @commands.command()
    async def view(self, ctx, id = None):
        if id == None:
            query : database.TutorBot_Sessions = database.TutorBot_Sessions.select().where(database.TutorBot_Sessions.TutorID == ctx.author.id)

            embed = discord.Embed(title = "Scheduled Tutor Sessions", color = discord.Color.dark_blue())
            embed.add_field(name = "Schedule:", value = f"{ctx.author.name}'s Schedule:")

            ListTen = []
            i = 0
            for entry in query:
                studentUser = await self.bot.fetch_user(entry.StudentID)
                ListTen.append(f"{self.RepeatEmoji[entry.Repeat]} `{entry.SessionID}`-{entry.Date} {entry.Time} -> {studentUser.name}")



        else:
            entry = database.TutorBot_Sessions.select().where(database.TutorBot_Sessions.SessionID == id)
            if entry.exists():
                entry = entry.get()

                studentUser = await self.bot.fetch_user(entry.StudentID)
                embed = discord.Embed(title = "Tutor Session Query", description = f"{self.RepeatEmoji[entry.Repeat]} `{entry.SessionID}`-{entry.Date} {entry.Time} -> {studentUser.name}")
            else:
                embed = discord.Embed(title = "Invalid Session", description = "This session does not exist, please check the ID you've provided!", color = discord.Color.red())
                await ctx.send(embed = embed)

    #@commands.command()
    #async def get(self, ctx, id):

    #@commands.command()
    #async def reqtutor(self, ctx, date, time, timezone, id, repeats):

    #@commands.command()
    #async def reqinterview(self, ctx):

def setup(bot):
    bot.add_cog(TutorBotStaffCMD(bot))


