from tkinter import Entry
import discord
from core import database
from discord.ext import commands, tasks


class TutorBotStaffCMD(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.RepeatEmoji = {
            True: ":black_large_square:" ,
            False: "🔁"
        }

    @commands.command()
    async def view(self, ctx, id = None):
        if id == None:
            query : database.TutorBot_Sessions = database.TutorBot_Sessions.select().where(database.TutorBot_Sessions.SessionID == id)

            embed = discord.Embed(title = "Scheduled Tutor Sessions", color = discord.Color.dark_blue())
            embed.add_field(name = "Schedule:", value = f"{ctx.author.name}'s Schedule:")

            ListTen = []
            for entry in query:
                studentUser = await self.bot.fetch_user(entry.StudentID)
                ListTen.append(f"{self.RepeatEmoji[entry.Repeat]} `{entry.SessionID}`-{entry.Date} {entry.Time} -> {studentUser.name}")
                


        else:
            query = database.TutorBot_Sessions.select().where(database.TutorBot_Sessions.SessionID == id)
            querySKIP = database.TutorBot_SkippedSessions.select().where(database.TutorBot_SkippedSessions.SessionID == id)

            embed = discord.Embed(title = "Tutor Session Query", description = "")
            if query.exists() and querySKIP.exists():
                pass
            elif query.exists() and not querySKIP.exists():
                pass
            elif not query.exists():
                pass

    @commands.command()
    async def get(self, ctx, id):
        pass
        

    #@commands.command()
    #async def reqtutor(self, ctx, date, time, timezone, id, repeats):

    #@commands.command()
    #async def reqinterview(self, ctx):

def setup(bot):
    bot.add_cog(TutorBotStaffCMD(bot))


