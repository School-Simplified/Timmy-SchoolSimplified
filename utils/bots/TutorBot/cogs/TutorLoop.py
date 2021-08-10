from datetime import datetime

import discord
import pytz
from core import database
from discord.ext import commands, tasks


class TutorBotLoop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @tasks.loop(seconds=60.0)
    async def voiceCheck(self):
        now = datetime.utcnow()
        for entry in database.TutorBot_Sessions:
            if (datetime.utcnow() - entry.Date).seconds > 300:
                continue
            else:
                tutor = await self.bot.fetch_user(entry.TutorID)
                student = await self.bot.fetch_user(entry.StudentID)

                botch = await self.bot.fetch_user(862480236965003275)

                embed = discord.Embed(title = "ALERT: You have a Tutor Session Soon!", description = "Please make sure you both communicate and set up a private voice channel!", color = discord.Color.green())
                embed.add_field(name = "Tutor Session Details", value = f"**Tutor:** {tutor.name}\n**Student:** {student.name}\n**Session ID:** {entry.SessionID}\n**Time:** {entry.Time}")
                
                try:
                    await tutor.send(embed = embed)
                except:
                    await botch.send("Unable to send a reminder DM to you {tutor.mention}!", embed = embed)
                try:
                    await student.send(embed = embed)
                except:
                    print(f"Unable to Send a Reminder DM to: {student.id}")

        #M = now.strftime("%p")
        #Time = now.strftime("%-I:%-M")
        #Date = now.strftime("%-m/%-d/%Y")

        #(database.TutorBot_Sessions.Date == Date) & (database.TutorBot_Sessions.Time == Time) & (database.TutorBot_Sessions.AMorPM == M)
        #query = database.TutorBot_Sessions.select().where((database.TutorBot_Sessions.Date == Date) & (database.TutorBot_Sessions.Time == Time))
        
        #if query.exists():
        #    pass

def setup(bot):
    bot.add_cog(TutorBotLoop(bot))


