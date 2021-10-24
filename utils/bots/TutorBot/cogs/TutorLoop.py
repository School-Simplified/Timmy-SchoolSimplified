from datetime import datetime, timedelta

import discord
import pytz
from core import database
from discord.ext import commands, tasks

class TutorBotLoop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.est = pytz.timezone('US/Eastern')
        self.tutorsession.start()

    def cog_unload(self):
        self.tutorsession.cancel()

    @tasks.loop(seconds=60.0)
    async def tutorsession(self): 
        now = datetime.now(self.est)
        for entry in database.TutorBot_Sessions: 
            TutorSession = pytz.timezone("America/New_York").localize(entry.Date)
            val = int((TutorSession - now).total_seconds())

            if val <= 120 and val >= 1:
                print(entry.TutorID, entry.StudentID)
                tutor = self.bot.get_user(entry.TutorID)
                student = self.bot.get_user(entry.StudentID)

                if tutor == None:
                    tutor = await self.bot.fetch_user(entry.TutorID)
                if student == None:
                    student = await self.bot.fetch_user(entry.StudentID)

                print(tutor, student)
                botch = self.bot.get_channel(862480236965003275)
                embed = discord.Embed(title = "ALERT: You have a Tutor Session Soon!", description = "Please make sure you both communicate and set up a private voice channel!", color = discord.Color.green())
                embed.add_field(name = "Tutor Session Details", value = f"**Tutor:** {tutor.name}\n**Student:** {student.name}\n**Session ID:** {entry.SessionID}\n**Time:** {entry.Time}")
                
                try:
                    await tutor.send(embed = embed)
                except:
                    await botch.send(f"Unable to send a reminder DM to you {tutor.mention}!", embed = embed)
                try:
                    await student.send(embed = embed)
                except:
                    print(f"Unable to Send a Reminder DM to: {student.id}")
                
                geten: database.TutorBot_Sessions = database.TutorBot_Sessions.select().where(database.TutorBot_Sessions.id == entry.id).get()
                
                if geten.Repeat:
                    old = geten.Date
                    new = timedelta(days=7)
                    nextweek = old + new
                    geten.Date = nextweek
                    
                geten.ReminderSet = True
                geten.save()

            elif val < 0 and not entry.Repeat:
                geten: database.TutorBot_Sessions = database.TutorBot_Sessions.select().where(database.TutorBot_Sessions.id == entry.id).get()
                geten.delete_instance()

            elif val < 0 and entry.Repeat:
                query: database.TutorBot_Sessions = database.TutorBot_Sessions.select().where(database.TutorBot_Sessions.id == entry.id).get()
                print(query.id, val, entry.Repeat)
                old = query.Date
                new = timedelta(days=7)
                nextweek = old + new

                nw = nextweek.strftime("%m/%d/%Y")

                query.Date = nextweek
                query.save()



    @tutorsession.before_loop
    async def before_printer(self):
        print('Starting Tutor Loop')
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(TutorBotLoop(bot))


